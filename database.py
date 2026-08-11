from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config import DATABASE_PATH
from models.entities import Base, Question, Resource, Roadmap, Unit


DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{DATABASE_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def initialize_database() -> None:
    Base.metadata.create_all(engine)
    with SessionFactory.begin() as session:
        if session.scalar(select(Roadmap.id).limit(1)) is not None:
            return
        roadmap = Roadmap(id="programming-basics", title="Programming Basics")
        session.add(roadmap)
        units = [
            ("variables", "Variables and types"),
            ("conditions", "Conditions"),
            ("loops", "Loops"),
            ("functions", "Functions"),
            ("collections", "Collections"),
            ("errors", "Error handling"),
        ]
        for order, (unit_id, title) in enumerate(units, 1):
            session.add(Unit(id=unit_id, roadmap_id=roadmap.id, title=title, order=order))
            session.add(Resource(
                id=f"res-{unit_id}", unit_id=unit_id,
                url=f"https://docs.python.org/3/tutorial/{unit_id}.html", title=title,
            ))
            for number in range(1, 4):
                session.add(Question(
                    id=f"q-{unit_id}-{number}", unit_id=unit_id,
                    text=f"{title}: choose answer A ({number}/3)",
                    options=["A", "B", "C", "D"], correct_option_index=0,
                ))
