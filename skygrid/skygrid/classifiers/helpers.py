from mongoengine import fields

def check_update_valid(update_dict):
    if 'classifier_id' in update_dict:
        raise Exception('Could not update classifier id!')


def update_document(document, data_dict):

    def field_value(field, value):

        if field.__class__ in (fields.ListField, fields.SortedListField):
            return [
                field_value(field.field, item)
                for item in value
            ]
        if field.__class__ in (
            fields.EmbeddedDocumentField,
            fields.GenericEmbeddedDocumentField,
            fields.ReferenceField,
            fields.GenericReferenceField
        ):
            return field.document_type(**value)
        else:
            return value

    [setattr(
        document, key,
        field_value(document._fields[key], value)
    ) for key, value in data_dict.items()]

    return document
