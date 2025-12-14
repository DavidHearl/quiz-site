from .models import *

def counts(request):
    # Get category counts for General Knowledge subcategories
    general_count = 0
    science_count = 0
    geography_count = 0
    history_count = 0
    entertainment_count = 0
    maths_count = 0
    mythology_count = 0
    technology_count = 0
    sport_count = 0
    
    try:
        general_cat = GeneralKnowledgeCategory.objects.get(category='General')
        general_count = GeneralKnowledge.objects.filter(category=general_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        science_cat = GeneralKnowledgeCategory.objects.get(category='Science')
        science_count = GeneralKnowledge.objects.filter(category=science_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        geography_cat = GeneralKnowledgeCategory.objects.get(category='Geography')
        geography_count = GeneralKnowledge.objects.filter(category=geography_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        history_cat = GeneralKnowledgeCategory.objects.get(category='History')
        history_count = GeneralKnowledge.objects.filter(category=history_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    # Entertainment now includes both Entertainment and Pop Culture
    try:
        entertainment_cat = GeneralKnowledgeCategory.objects.get(category='Entertainment')
        entertainment_count = GeneralKnowledge.objects.filter(category=entertainment_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        pop_culture_cat = GeneralKnowledgeCategory.objects.get(category='Pop Culture')
        entertainment_count += GeneralKnowledge.objects.filter(category=pop_culture_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        maths_cat = GeneralKnowledgeCategory.objects.get(category='Maths')
        maths_count = GeneralKnowledge.objects.filter(category=maths_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        mythology_cat = GeneralKnowledgeCategory.objects.get(category='Mythology')
        mythology_count = GeneralKnowledge.objects.filter(category=mythology_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        technology_cat = GeneralKnowledgeCategory.objects.get(category='Technology')
        technology_count = GeneralKnowledge.objects.filter(category=technology_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        sport_cat = GeneralKnowledgeCategory.objects.get(category='Sport')
        sport_count = GeneralKnowledge.objects.filter(category=sport_cat).count()
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    return {
        'general_knowledge_count': GeneralKnowledge.objects.count(),
        'general_count': general_count,
        'science_count': science_count,
        'geography_count': geography_count,
        'history_count': history_count,
        'entertainment_count': entertainment_count,
        'maths_count': maths_count,
        'mythology_count': mythology_count,
        'technology_count': technology_count,
        'sport_count': sport_count,
        'true_or_false_count': TrueOrFalse.objects.count(),
        'flags_count': Flags.objects.count(),
        'logos_count': Logos.objects.count(),
        'jets_count': Jets.objects.count(),
        'celebrities_count': Celebrities.objects.count(),
        'movies_count': Movies.objects.count(),
        'locations_count': Locations.objects.count(),
        'music_count': Music.objects.count(),
    }