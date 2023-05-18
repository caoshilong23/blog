from django.http import JsonResponse

def cors_test(request):
    return JsonResponse({'msg':'cors is ok'})