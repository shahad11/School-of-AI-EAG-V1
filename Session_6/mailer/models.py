from pydantic import BaseModel, EmailStr
from typing import List, Optional


class FetchAINewsInput(BaseModel):
    url: Optional[str] = None


class Article(BaseModel):
    title: str
    url: str


class FetchAINewsOutput(BaseModel):
    articles: List[Article]


class FetchArticleContentInput(BaseModel):
    url: str


class FetchArticleContentOutput(BaseModel):
    content: str


class ArticleContent(BaseModel):
    title: str
    content: str


class SaveToWordInput(BaseModel):
    filename: str
    articles: List[ArticleContent]


class SaveToWordOutput(BaseModel):
    message: str


class SendEmailInput(BaseModel):
    subject: str
    body: str
    to_email: EmailStr


class SendEmailOutput(BaseModel):
    message: str


