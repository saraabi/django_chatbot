import json
import openai
import urllib

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

from .models import Question, Answer, UserProfile

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


    def gpt3(self, prompt, model='text-davinci-003', response_length=512, 
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