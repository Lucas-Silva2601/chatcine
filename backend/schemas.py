"""
Schemas Marshmallow para validação e serialização de dados JSON.
"""
from marshmallow import Schema, fields, validate, ValidationError
from typing import Any


class MovieContentSchema(Schema):
    """Schema para conteúdo de filme identificado pela IA."""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    year = fields.Str(required=True, validate=validate.Length(min=4, max=4))


class RecommendationItemSchema(Schema):
    """Schema para item de recomendação."""
    title = fields.Str(required=True)
    year = fields.Str(required=True)


class AIResponseSchema(Schema):
    """Schema para resposta da IA."""
    type = fields.Str(
        required=True,
        validate=validate.OneOf(['movie', 'recommendations', 'text'])
    )
    content = fields.Raw(required=True)
    
    @staticmethod
    def validate_content_by_type(data: dict[str, Any]) -> None:
        """Valida o conteúdo baseado no tipo da resposta."""
        response_type = data.get('type')
        content = data.get('content')
        
        if response_type == 'movie':
            # Valida estrutura de filme
            if not isinstance(content, dict):
                raise ValidationError('Content deve ser um objeto para tipo "movie".')
            MovieContentSchema().load(content)
        elif response_type == 'recommendations':
            # Valida lista de recomendações
            if not isinstance(content, list):
                raise ValidationError('Content deve ser uma lista para tipo "recommendations".')
            for item in content:
                RecommendationItemSchema().load(item)
        elif response_type == 'text':
            # Valida texto
            if not isinstance(content, str):
                raise ValidationError('Content deve ser uma string para tipo "text".')


def validate_ai_response(data: dict[str, Any]) -> dict[str, Any]:
    """
    Valida resposta da IA usando schema Marshmallow.
    
    Args:
        data: Dicionário com resposta da IA
        
    Returns:
        Dados validados
        
    Raises:
        ValidationError: Se os dados não são válidos
    """
    # Valida estrutura básica
    schema = AIResponseSchema()
    validated = schema.load(data)
    
    # Valida conteúdo baseado no tipo
    AIResponseSchema.validate_content_by_type(validated)
    
    return validated

