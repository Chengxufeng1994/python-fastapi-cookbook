from datetime import date, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Query


def check_start_end_condition(start: date, end: date):
    if start > end:
        raise HTTPException(status_code=400, detail="End date must be greater than start date")


def time_range(
    start: date = Query(
        default=date.today(),
        description="If not provided the current date is used",
        examples=[
            date.today().isoformat(),
        ],
    ),
    end: date = Query(
        None,
        examples=[
            date.today() + timedelta(days=7),
        ],
    ),
):
    check_start_end_condition(start, end)
    return start, end


time_range_dep = Annotated[tuple, Depends(time_range)]


def select_category(
    category: Annotated[
        str,
        Path(
            description=("Kind of travel you are interested in"),
            enum=[
                "cruises",
                "city-breaks",
                "resort-stays",
            ],
        ),
    ],
) -> str:
    return category


def check_coupon_validity(
    category: Annotated[str, Depends(select_category)],
    code: str | None = Query(None, description="Coupon code"),
) -> bool:
    coupon_dict = {
        "cruises": "CRUISE10",
        "city-breaks": "CITYBREAK15",
        "resort-stays": "RESORT20",
    }
    if code is not None and coupon_dict.get(category, ...) == code:
        return True
    return False


class CommonQueryParams:
    def __init__(
        self,
        category: Annotated[
            str | None,
            Path(
                description=("Kind of travel " "you are interested in"),
                enum=[
                    "cruises",
                    "city-breaks",
                    "resort-stays",
                ],
            ),
        ],
        start: Annotated[
            date | None,
            Query(
                description="required if end date is not provided",
                examples=["2023-01-01"],
            ),
        ] = None,
        end: Annotated[
            date | None,
            Query(
                description="required if start date is not provided",
                examples=["2023-01-01"],
            ),
        ] = None,
        code: str | None = Query(None, description="Coupon code"),
    ):
        if start is None or end is None:
            raise HTTPException(status_code=400, detail="Start and end date are required")
        check_start_end_condition(start, end)
        self.start = start
        self.end = end
        self.category = category
        self.applicable_discount = check_coupon_validity(category or "", code)
