from fastapi import APIRouter

router = APIRouter(
    prefix="/api/user",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/login", tags=["users"])
async def login():
    # todo
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/login", tags=["users"])
async def register():
    # todo
    return [{"username": "Rick"}, {"username": "Morty"}]