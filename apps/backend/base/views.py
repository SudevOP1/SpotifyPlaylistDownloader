from django.http import JsonResponse

def hello(request):
    return JsonResponse({"success": True, "message": "Hello",})

