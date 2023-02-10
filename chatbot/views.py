import json
import openai
import urllib

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

from .models import Question, Answer, UserProfile

class Home(ListView):
    model = Answer

class CreateAnswer(CreateView):
    model = Answer

class Chat(DetailView):
    model = UserProfile
    template_name = 'chatbot/userprofile_detail.html'

    def post(self, request, **kwargs):
        openai.api_key = settings.OPENAI_API_KEY
        self.object = self.get_object()
        print(self.object)
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
        return render(request, self.template_name, context)


    def gpt3(self, prompt, engine='davinci', response_length=64, 
        temperature=0.9, top_p=1, frequency_penalty=1, presence_penalty=1, 
        start_text='\nAI:', restart_text='\nHuman: ', stop_seq=["\nHuman:", "\n"]):
        openai.api_key = settings.OPENAI_API_KEY
        print('here')
        print(prompt)
        response = openai.Completion.create(
            prompt=prompt + start_text,
            engine=engine,
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