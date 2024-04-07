from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select, Field, Relationship
from typing import Annotated, Optional, List
from quizapi import settings

class CreateUser(SQLModel) :
    name: str
    email: str | None = None

class ResponseUser(SQLModel) :
    id : int
    name : str
    email : str   

class CreateQuestion(SQLModel) :
    text : str
    type : str

class ResponseQuestion(SQLModel) :
    id : int
    text : str
    type : str   

class CreateOptions(SQLModel) :
    question_id : int
    option_text : str

class ResponseOptions(SQLModel) :
    id : int
    question_id : int
    option_text : str    
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str | None

class CreateAnswers(SQLModel) :
    selected_option : str
    question_id : int
    user_id : int

class ResponseAnswers(SQLModel) :
    id  : int
    question_id : int
    selected_option : str
    user_id : int    
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


connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(connection_string, connect_args = {"sslmode": "require" }
, pool_recycle = 300)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("creating_tables....")
    create_db_and_tables()
    yield    


app : FastAPI = FastAPI(lifespan=lifespan,title="Quiz APP", 
version="0.0.1")

servers = [
    {
            "url":"http://127.0.0.1:8000",
            "description" : "production server" },

            {
                 "url" : "https://localhost 3000",
            "description" : "devolpment server"
            },
            ] 


# Dependemcy injection
def get_session():
    with Session(engine) as session:
        yield session
    

# get all users 
@app.get("/users", response_model = List[User])
def read_users(session : Annotated[Session, Depends(get_session)]) :
    users = session.exec(select(User)).all()
    return users

# get users by id
@app.get("/users/{id}")
def read_users_by_id(id : int, session : Annotated[Session, Depends(get_session)]) :
    users = session.get(User, id)
    if not users :
        raise HTTPException(status_code=404, detail="User not found")
    return users

# post method for users
@app.post("/users", response_model = ResponseUser)
def post_users(user : CreateUser, sesssion : Annotated[Session, Depends(get_session)]) :
    user_post = User(name = user.name, email = user.email)
    sesssion.add(user_post)
    sesssion.commit()
    sesssion.refresh(user_post)
    return user_post

# patch method for users
@app.patch("/user/{user_id}", response_model = ResponseUser)
def patch_users(user_id : int, user : CreateUser, session : Annotated[Session, Depends(get_session)]) :
    user_patch = session.get(User, user_id)
    if not user_patch :
        raise HTTPException(status_code=404, detail="User not found")
    user_patch.name = user.name
    user_patch.email = user.email
    session.commit()
    session.refresh(user_patch)
    return user_patch

# delete method for users
@app.delete("/user/{user_id}")
def delete_users(user_id : int, session : Annotated[Session, Depends(get_session)]) :
    user_delete = session.get(User, user_id)
    if not user_delete :
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user_delete)
    session.commit()
    return {"message" : "User deleted successfully"}    

# get all questions
@app.get("/questions", response_model=List[Question])
def read_questions(session : Annotated[Session, Depends(get_session)]) :
    get_questions = session.exec(select(Question)).all()
    return get_questions

# get questions by id
@app.get("/questions/{id}", response_model = ResponseQuestion)
def read_question_by_id(id : int, session: Annotated[Session, Depends(get_session)]) : 
    get_questions_by_id = session.get(Question, id) 
    if not get_questions_by_id :
        raise HTTPException(status_code=404, detail="Question not found")
    return get_questions_by_id 

# post method for questions
@app.post("/questions", response_model = ResponseQuestion)
def post_questions(question : CreateQuestion, session : Annotated[Session, Depends(get_session)]) :
    post_question = Question(text = question.text, type = question.type)
    session.add(post_question)
    session.commit()
    session.refresh(post_question)  
    return post_question

#patch method for questions
@app.patch("/questions/{id}", response_model = ResponseQuestion)
def patch_qusetions(id : int, question : CreateQuestion, session : Annotated[Session,  Depends(get_session)]) :
    update_question = session.get(Question, id)
    if not update_question :
        raise HTTPException(status_code = 404, detail="Question not found") 
    update_question.text = question.text
    update_question.type = question.type
    session.commit()
    session.refresh(update_question)
    return update_question

# delete method for questions
@app.delete("/questions/{id}")
def delete_questions(id : int, session : Annotated[Session, Depends(get_session)]) :
    delete_question = session.get(Question, id)
    if not delete_question :
        raise HTTPException(status_code=404, detail="Question not found")
    session.delete(delete_question)
    session.commit()
    return {"message" : "Question deleted successfully"}

# get all Options
@app.get("/options", response_model = List[Options])
def read_options(session : Annotated[Session, Depends(get_session)]) :
    get_options = session.exec(select(Options)).all()
    return get_options

# get options by id
@app.get("/options/{id}", response_model = ResponseOptions)
def read_options_by_id(id : int, session : Annotated[Session, Depends(get_session)]) :
    get_options_by_id = session.get(Options, id)
    if not get_options_by_id :
        raise HTTPException(status_code=404, detail="Options not found")
    return get_options_by_id

# post method for options
@app.post("/options", response_model = ResponseOptions)
def post_options(option : CreateOptions, session : Annotated[Session, Depends(get_session)]) :
    post_options = Options(question_id = option.question_id, option_text = option.option_text)
    session.add(post_options)
    session.commit()
    session.refresh(post_options)
    return post_options

# patch method for options
@app.patch("/options/{id}", response_model = ResponseOptions)
def patch_options(id : int, option : CreateOptions, session : Annotated[Session, Depends(get_session)]) :
    update_option = session.get(Options, id)
    if not update_option :
        raise HTTPException(status_code=404, detail="Options not found")
    update_option.question_id = option.question_id
    update_option.option_text = option.option_text
    session.commit()
    session.refresh(update_option)
    return update_option

# delete method for options
@app.delete("/options/{id}")
def delete_options(id : int, session : Annotated[Session, Depends(get_session)]) :
    delete_option = session.get(Options, id)
    if not delete_option :
        raise HTTPException(status_code=404, detail="Options not found")
    session.delete(delete_option)
    session.commit()
    return {"message" : "Options deleted successfully"}

# get all answers
@app.get("/answers", response_model = List[Answers])
def read_answers(session : Annotated[Session, Depends(get_session)]) :
    get_answers = session.exec(select(Answers)).all()
    return get_answers

# get answers by id
@app.get("/answers/{id}", response_model = ResponseAnswers)
def read_answers_by_id(id : int, session : Annotated[Session, Depends(get_session)]) :
    get_answers_by_id = session.get(Answers, id)
    if not get_answers_by_id :
        raise HTTPException(status_code=404, detail="Answers not found")
    return get_answers_by_id

# post method for answers
@app.post("/answers", response_model = ResponseAnswers)
def post_answers(answer : CreateAnswers, session : Annotated[Session, Depends(get_session)]) :
    post_answers = Answers(selected_option = answer.selected_option, 
    question_id = answer.question_id, 
    user_id = answer.user_id )
    session.add(post_answers)
    session.commit()
    session.refresh(post_answers)
    return post_answers

# patch method for answers
@app.patch("/answers/{id}", response_model = ResponseAnswers)
def patch_answers(id : int, answer : CreateAnswers, session : Annotated[Session, Depends(get_session)]) :
    update_answer = session.get(Answers, id)
    if not update_answer :
        raise HTTPException(status_code=404, detail="Answers not found")
    update_answer.selected_option = answer.selected_option
    update_answer.question_id = answer.question_id
    session.commit()
    session.refresh(update_answer)
    return update_answer

# delete method for answers
@app.delete("/answers/{id}")
def delete_answers(id : int, session : Annotated[Session, Depends(get_session)]) :
    delete_answer = session.get(Answers, id)
    if not delete_answer :
        raise HTTPException(status_code=404, detail="Answers not found")
    session.delete(delete_answer)
    session.commit()
    return {"message" : "Answers deleted successfully"}