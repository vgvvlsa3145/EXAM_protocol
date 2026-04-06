from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(str(key))

@register.simple_tag
def is_selected(saved_answers, question_id, option_id):
    """
    Returns 'checked' if the saved answer for question_id matches option_id.
    Handles potential type mismatches (str vs int).
    """
    if not saved_answers:
        return ""
    
    # Convert keys/values to strings for robust comparison
    s_qid = str(question_id)
    s_oid = str(option_id)
    
    val = saved_answers.get(s_qid)
    if val and str(val) == s_oid:
        return "checked"
    return ""

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})
