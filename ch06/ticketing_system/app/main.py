from contextlib import asynccontextmanager
from typing import Annotated

from app.database import Base
from app.db_connection import get_db_session, get_engine
from app.operations import (
    create_event,
    create_ticket,
    delete_ticket,
    get_ticket,
    update_ticket_price,
)
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
    await engine.dispose()


app = FastAPI(
    title="Ticketing System",
    description="A simple API to manage tickets",
    version="0.1.0",
    lifespan=lifespan,
)


class TicketRequest(BaseModel):
    price: float | None
    show: str | None
    user: str | None = None


@app.post("/ticket", response_model=dict[str, int])
async def create_ticket_route(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    ticket: TicketRequest,
):
    if ticket.show is None:
        raise HTTPException(status_code=400, detail="Show is required")

    ticket_id = await create_ticket(
        db_session,
        ticket.show,
        ticket.user,
        ticket.price,
    )
    return {"ticket_id": ticket_id}


@app.get("/ticket/{ticket_id}")
async def read_ticket(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    ticket_id: int,
):
    ticket = await get_ticket(db_session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.put("/ticket/{ticket_id}/price/{new_price}")
async def update_ticket_price_route(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    ticket_id: int,
    new_price: float,
):
    updated = await update_ticket_price(db_session, ticket_id, new_price)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"detail": "Price updated"}


@app.delete("/ticket/{ticket_id}")
async def delete_ticket_route(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    ticket_id: int,
):
    ticket = await delete_ticket(db_session, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"detail": "Ticket removed"}


@app.post("/event")
async def create_event_route(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    event_name: str,
    nb_tickets: int | None = 0,
):
    event_id = await create_event(db_session, event_name, nb_tickets)
    return {"event_id": event_id}
