from rest_framework import viewsets, generics

from .views import *


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()


class TextAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = TextSerializer
    queryset = TextAnswer.objects.all()


class RatingAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    queryset = RatingAnswer.objects.all()


class MCQAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = MCQSerializer
    queryset = MCQAnswer.objects.all()


class QuestionViewSet(viewsets.ModelViewSet):
    """
    view set for question: lists all the question asked by user
    """
    serializer_class = QuestionSerializer
    queryset = QuestionDB.objects.all()

    def get_queryset(self, **kwargs):
        if not self.request.user.is_superuser:
            queryset = QuestionDB.objects.filter(asked_by=self.request.user)
            return queryset
        else:
            queryset = QuestionDB.objects.all()
            return queryset


class QuestionSet(generics.ListCreateAPIView):
    """
    custom view set to add question in survey
    """
    serializer_class = QuestionSerializer
    model = QuestionDB
    lookup_field = "rel_question"

    def perform_create(self, serializer):
        """
        overridden method to link question to survey and user with question
        :param serializer: serialized data of question model
        :return: None
        """
        survey_obj = Survey.objects.get(id=self.kwargs['rel_question'])
        que_obj = serializer.save()
        que_obj.asked_by.add(self.request.user)
        survey_obj.question.add(que_obj)

    def get_queryset(self, *args, **kwargs):
        if 'rel_question' in self.kwargs:
            queryset = self.model.objects.filter(rel_question=self.kwargs['rel_question'])
        else:
            queryset = self.model.objects.filter(rel_question__created_by=self.request.user)
        return queryset


class SurveyViewSet(viewsets.ModelViewSet):
    """
    view set for survey
    """
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    def get_queryset(self):
        if not self.request.user.is_superuser:
            queryset = Survey.objects.filter(created_by=self.request.user)
            return queryset
        else:
            queryset = Survey.objects.all()
            return queryset
