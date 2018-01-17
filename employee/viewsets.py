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

    def perform_create(self, serializer):
        que_obj = serializer.save()
        que_obj.asked_by.add(self.request.user)
        if que_obj.answer_type == 0:  # MCQ
            que_obj.content_type = ContentType.objects.get_for_model(MCQAnswer)
        if que_obj.answer_type == 1:  # Rating
            que_obj.content_type = ContentType.objects.get_for_model(RatingAnswer)
        if que_obj.answer_type == 2:  # TextField
            que_obj.content_type = ContentType.objects.get_for_model(TextAnswer)
        que_obj.save()

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
        if que_obj.answer_type == 0:  # MCQ
            que_obj.content_type = ContentType.objects.get_for_model(MCQAnswer)
        if que_obj.answer_type == 1:  # Rating
            que_obj.content_type = ContentType.objects.get_for_model(RatingAnswer)
        if que_obj.answer_type == 2:  # TextField
            que_obj.content_type = ContentType.objects.get_for_model(TextAnswer)
        que_obj.save()
        survey_obj.question.add(que_obj)

    def get_queryset(self, *args, **kwargs):
        if 'rel_question' in self.kwargs:
            queryset = self.model.objects.filter(rel_question=self.kwargs['rel_question'])
        else:
            queryset = self.model.objects.filter(rel_question__created_by=self.request.user)
        return queryset


class SurveyViewSet(viewsets.ModelViewSet):
    """ Survey API to list, add, modify survey """
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    def get_queryset(self):
        current_user = self.request.user
        if not current_user.is_superuser:
            if current_user.role in [1, 2]:
                queryset = Survey.objects.filter(created_by=current_user)
            else:
                queryset = Survey.objects.filter(created_by__rel_company_user=current_user.employee.company_name, complete=True)
            return queryset
        else:
            queryset = Survey.objects.all()
            return queryset


class SurveyResponseViewSet(viewsets.ModelViewSet):
    """ API for saving response of survey """
    serializer_class = SurveyResponseSerializer
    queryset = SurveyResponse.objects.all()


class NewsFeedViewSet(viewsets.ModelViewSet):
    """ API for creating and listing news feed """
    serializer_class = NewsFeedSerializer
    queryset = NewsFeed.objects.all()

    def get_queryset(self):
        current_user = self.request.user
        if not current_user.is_superuser:
            if current_user.role in [1, 2]:
                queryset = NewsFeed.objects.filter(created_by=current_user)
            else:
                queryset = NewsFeed.objects.filter(created_by__rel_company_user=current_user.employee.company_name)
            return queryset
        else:
            queryset = NewsFeed.objects.all()
            return queryset
