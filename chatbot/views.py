import json
import openai
import urllib
from base64 import urlsafe_b64decode

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView


from allauth.socialaccount.models import SocialToken, SocialApp
from allauth.socialaccount.signals import social_account_added
from bs4 import BeautifulSoup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .models import Question, Answer, UserProfile, Thread

class Home(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'home.html'

    def get_object(self):
        return self.request.user.userprofile
    
    def post(self, request, **kwargs):
        userprofile = self.get_object()
        userprofile.description = request.POST.get('description')
        userprofile.save()
        return redirect(reverse('home'))


class CreateAnswer(CreateView):
    model = Answer

class HarvestEmails(View):

    def get(self, request, **kwargs):
        app = SocialApp.objects.get(provider='google')
        token = SocialToken.objects.get(account__user=request.user)
        credentials = Credentials(
            token=token.token,
            refresh_token=token.token_secret,
            client_id=app.client_id,
            client_secret=app.secret,
        )
        service = build('gmail', 'v1', credentials=credentials)
        result = service.users().threads().list(userId=request.user.email, q='min:2 from:{}'.format(request.user.email)).execute()
        # result = service.users().messages().list(userId=request.user.email).execute()
        messages = [ ]
        if 'messages' in result:
            print('messages!!')
            messages.extend(result['threads'])
        emails = self.get_emails(service, result)
        data = {
            'emails': emails
        }
        return render(request, 'harvest_emails.html', data)

    def get_emails(self, service, query):
        emails = []
        for email in query['threads']:
            emails.append(self.get_email(service, email))
        return emails
    
    def get_email(self, service, query):
        thread = service.users().threads().get(userId=self.request.
        user.email, id=query['id'], format='full').execute()
        print(thread.keys())
        thread = Thread.objects.create(
            gmail_id=thread.get('id'),
        )
        email_list = []
        for msg in thread['messages']:
            payload = msg['payload']
            pring(msg.keys())
            headers = payload.get("headers")
            parts = payload.get("parts")
            email_dict = {}
            if headers:
                for header in headers:
                    name = header.get("name")
                    value = header.get("value")
                    for i in ['_from', 'to', 'subject', 'date']:
                        if name.lower() == i:
                            email_dict[i] = value
            if parts:
                for part in parts:
                    body = part.get('body')
                    if body:
                        if body.get('data'):
                            data = urlsafe_b64decode(body.get('data')).decode()
                            soup = BeautifulSoup(data, features="html.parser")
                            email_dict['body'] = soup.get_text()
            email_list.append(email_dict)
            thread.create_emails(email_dict)
        return email_list

    
class Chat(DetailView):
    model = UserProfile
    template_name = 'chatbot/userprofile_detail.html'

    def post(self, request, **kwargs):
        openai.api_key = settings.OPENAI_API_KEY
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        question = Question.objects.create(
            name=request.POST['question'],
            user=context['userprofile'],
        )
        answer, prompt = self.gpt3(prompt=request.POST['question'])
        context['answer'] = answer
        context['prompt'] = prompt
        answer = Answer.objects.create(
            question=question,
            text=answer,
            user=context['userprofile'],
        )
        print(context) 
        return redirect(reverse('home'))
        # return render(request, self.template_name, context)


    def gpt3(self, prompt, model='text-davinci-003', response_length=1024, 
        temperature=0.9, top_p=1, frequency_penalty=1, presence_penalty=1, 
        start_text='\nAI:', restart_text='\nHuman: ', stop_seq=["\nHuman:", "\n"]):
        openai.api_key = settings.OPENAI_API_KEY
        if self.get_object().description:
            description = self.get_object().description
        else:
            description = "friendly AI assistant chatbot."
        
        # prompt = """The following is a conversation with an AI assistant.\nHuman: Who are you?
        #     AI: I am {0}
        #     Human: {1}""".format(description, prompt)
        # print(prompt)
        prompt = self.get_object().build_prompt()
        print(prompt)
        response = openai.Completion.create(
            prompt=prompt + start_text,
            model=model,
            max_tokens=response_length,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop_seq,
        )
        print(response)
        answer = response.choices[0]['text']
        new_prompt = prompt + start_text + answer + restart_text
        return answer, new_prompt