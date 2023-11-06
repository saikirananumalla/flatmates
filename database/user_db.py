from sqlalchemy.orm import Session

from schema import user_schema


# def get_user_by_user_name(db: Session, user_name: str):
#     return (
#         db.query(user_model.User).filter(user_model.User.user_name == user_name).first()
#     )
#
#
# def get_user_by_email(db: Session, email: str):
#     return db.query(user_model.User).filter(user_model.User.email == email).first()
#
#
# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(user_model.User).offset(skip).limit(limit).all()
#
#
# def create_user(db: Session, user: user_schema.User):
#     db_user = user_model.User(
#         email_id=user.email_id,
#         password=user.password,
#         phone=user.phone,
#         user_name=user.user_name,
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
