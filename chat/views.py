from employee.views import *
from main.views import *


class ChatView(LoginRequiredMixin, APIView):
    login_url = reverse_lazy('login')
    serializer_class = UserSerializer
    renderer_classes = [TemplateHTMLRenderer]
    success_url = reverse_lazy('chat')
    template_name = 'company/chat.html'
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request):
        serializer = self.serializer_class()
        return Response({'serializer': serializer})
