from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select, Field, Relationship
from typing import Annotated, Optional, List
from quizapi import settings

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str | None

class Question(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str = Field(index=True)
    type: str = Field(index=True)
    options: Optional[List["Options"]] = Relationship(back_populates="question")

class Options(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question_id: int | None = Field(default=None, foreign_key="question.id", nullable=True)
    option_text: str = Field(index=True)
    question: Optional[Question] = Relationship(back_populates="options")

class Answers(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    selected_option: str = Field(index=True)
    question_id: int | None = Field(default=None, foreign_key="question.id", nullable=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", nullable=True)
