from typing import List

from fastapi import APIRouter, Depends, HTTPException

from repository import StoryRepository
from schemas import StoryModel

story_router = APIRouter(
    prefix="/api",
    tags=["Истории"],
)


@story_router.get('/stories/search', response_model=List[StoryModel])
async def get_stories_search():
    stories_search = await StoryRepository.get_stories_search()
    return stories_search


@story_router.get('/stories', response_model=List[StoryModel])
async def get_all_stories():
    stories_search = await StoryRepository.get_all_stories()
    return stories_search
