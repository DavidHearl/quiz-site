from .models import *

def counts(request):
    return {
        'general_knowledge_count': GeneralKnowledge.objects.count(),
        'true_or_false_count': TrueOrFalse.objects.count(),
        'flags_count': Flags.objects.count(),
        'logos_count': Logos.objects.count(),
        'jets_count': Jets.objects.count(),
        'celebrities_count': Celebrities.objects.count(),
        'movies_count': Movies.objects.count(),
        'locations_count': Locations.objects.count(),
    }