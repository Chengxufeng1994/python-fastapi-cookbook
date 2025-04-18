from typing import Optional

from app.database import Event, Sponsor, Sponsorship, Ticket, TicketDetails
from sqlalchemy import and_, delete, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only


async def create_ticket(
    db_session: AsyncSession,
    show_name: str,
    user: Optional[str] = None,
    price: Optional[float] = None,
) -> int:
    ticket = Ticket(
        show=show_name,
        user=user,
        price=price,
        details=TicketDetails(),
    )
    async with db_session.begin():
        db_session.add(ticket)
        await db_session.flush()
        ticket_id = ticket.id
        await db_session.commit()
    return ticket_id


async def get_tickets(db_session: AsyncSession):
    async with db_session as sess:
        tickets = await sess.execute(select(Ticket))
        return tickets.scalars().all()


async def get_ticket(db_session: AsyncSession, ticker_id: int):
    stmt = select(Ticket).where(Ticket.id == ticker_id).options(joinedload(Ticket.details))
    async with db_session as sess:
        tickets = await sess.execute(stmt)
        return tickets.scalars().first()


async def get_all_tickets_for_show(db_session: AsyncSession, show: str):
    stmt = select(Ticket).options(joinedload(Ticket.details)).filter(Ticket.show == show)
    async with db_session as sess:
        tickets = await sess.execute(stmt)
        return tickets.scalars().all()


async def update_ticket_price(
    db_session: AsyncSession,
    ticket_id: int,
    new_price: float,
) -> bool:
    query = update(Ticket).where(Ticket.id == ticket_id).values(price=new_price)
    async with db_session as session:
        ticket_updated = await session.execute(query)
        await session.commit()
        if ticket_updated.rowcount == 0:
            return False
        return True


async def update_ticket(
    db_session: AsyncSession,
    ticket_id: int,
    update_ticket_dict: dict,
) -> bool:
    ticket_query = update(Ticket).where(Ticket.id == ticket_id)

    updating_ticket_values = update_ticket_dict.copy()

    if updating_ticket_values == {}:
        return False

    ticket_query = ticket_query.values(**updating_ticket_values)

    async with db_session as session:
        result = await session.execute(ticket_query)
        await session.commit()
        if result.rowcount == 0:
            return False

    return True


async def update_ticket_details(
    db_session: AsyncSession,
    ticket_id: int,
    updating_ticket_details: dict,
) -> bool:
    ticket_query = update(TicketDetails).where(TicketDetails.ticket_id == ticket_id)

    if updating_ticket_details == {}:
        return False

    ticket_query = ticket_query.values(**updating_ticket_details)

    async with db_session as session:
        result = await session.execute(ticket_query)
        await session.commit()
        if result.rowcount == 0:
            return False

    return True


async def delete_ticket(db_session: AsyncSession, id: int):
    result = await db_session.execute(
        delete(
            Ticket,
        ).where(Ticket.id == id)
    )
    await db_session.commit()
    if result.rowcount == 0:
        return False
    return True


async def create_event(
    db_session: AsyncSession, event_name: str, nb_tickets: int | None = 0
) -> int:
    async with db_session.begin():
        event = Event(name=event_name)
        db_session.add(event)
        await db_session.flush()
        event_id = event.id
        tickets = [
            Ticket(
                show=event_name,
                details=TicketDetails(seat=f"{n}A"),
                event_id=event_id,
            )
            for n in range(nb_tickets or 0)
        ]
        db_session.add_all(tickets)
        await db_session.commit()
    return event_id


async def create_sponsor(db_session: AsyncSession, sponsor_name: str) -> int:
    async with db_session.begin():
        sponsor = Sponsor(name=sponsor_name)
        db_session.add(sponsor)
        try:
            await db_session.flush()
        except IntegrityError:
            return 0
        sponsor_id = sponsor.id
        await db_session.commit()
    return sponsor_id


async def add_sponsor_to_event(
    db_session: AsyncSession,
    event_id: int,
    sponsor_id: int,
    amount: float,
) -> bool:
    query = text(
        "INSERT INTO sponsorships "
        "(event_id, sponsor_id, amount) "
        "VALUES (:event_id, :sponsor_id, :amount) "
        "ON CONFLICT (event_id, sponsor_id) "
        "DO UPDATE SET amount = "
        "sponsorships.amount + EXCLUDED.amount"
    )
    params = {
        "event_id": event_id,
        "sponsor_id": sponsor_id,
        "amount": amount,
    }

    async with db_session.begin():
        result = await db_session.execute(query, params)
        await db_session.commit()
        if result.rowcount == 0:
            return False
    return True


async def get_event(db_session: AsyncSession, event_id: int):
    async with db_session as session:
        result = await session.execute(
            select(Event).where(Event.id == event_id).options(joinedload(Event.sponsors))
        )
        event = result.scalars().first()
    return event


async def get_events_with_sponsors(
    db_session: AsyncSession,
):
    stmt = select(Event).options(joinedload(Event.sponsors))

    async with db_session as session:
        result = await session.execute(stmt)
        return result.unique().scalars().all()


async def get_event_sponsorships_with_amount(db_session: AsyncSession, event_id: int):
    stmt = (
        select(Sponsor.name, Sponsorship.amount)
        .join(Sponsorship, Sponsorship.sponsor_id == Sponsor.id)
        .where(Sponsorship.event_id == event_id)
        .order_by(Sponsorship.amount.desc())
    )

    async with db_session as session:
        result = await session.execute(stmt)
        sponsor_contributions = result.fetchall()
    return sponsor_contributions


async def get_events_tickets_with_user_price(db_session: AsyncSession, event_id: int):
    query = (
        select(Ticket)
        .where(Ticket.event_id == event_id)
        .options(load_only(Ticket.id, Ticket.user, Ticket.price))
    )
    async with db_session as session:
        result = await session.execute(query)
        tickets = result.scalars().all()
    return tickets


async def sell_ticket_to_user(
    db_session: AsyncSession,
    ticket_id: int,
    user: int,
) -> bool:
    query = (
        update(Ticket)
        .where(
            and_(
                Ticket.id == ticket_id,
                Ticket.sold.is_(False),
            )
        )
        .values(user=user, sold=True)
    )
    async with db_session as session:
        result = await session.execute(query)
        await session.commit()
        if result.rowcount == 0:
            return False
    return True
