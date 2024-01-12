from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from pymongo.server_api import ServerApi
import uuid

app = FastAPI()

uri = "mongodb+srv://<username>:<password>@svgcluster.ihjbljd.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['gamesDB']
collection = db['games']

class Game(BaseModel):
    name : str
    url : str
    author : str
    published_date : str

@app.post('/api/games/')
async def create_game(game : Game):
    insert = game.model_dump()
    insert['_id'] = str(uuid.uuid4())
    result = collection.insert_one(insert)
    return {**game.model_dump()}

@app.get('/api/games/')
async def get_all_games():
    games = [game for game in collection.find()]
    return games

@app.get('/api/games/{game_id}')
async def read_game(game_id : str):
    game = collection.find_one({'_id': str(game_id)})
    if game:
        return game
    raise HTTPException(status_code=404,detail="Game Not Found")

@app.put('/api/games/{game_id}')
async def update_game(game_id : str, updated_game : Game):
    updated_game = updated_game.dict(exclude_unset=True)
    result = collection.update_one({'_id':str(game_id)}, {'$set':updated_game})
    if result.modified_count == 1:
        return {**updated_game, '_id':game_id}
    raise HTTPException(status_code=404,detail="Game Not Found")

@app.delete('/api/games/{game_id}')
async def delete_game(game_id : str):
    result = collection.delete_one({'_id': str(game_id)})
    if result.deleted_count == 1:
        return {'message' : 'Game Deleted Successfully'}
    raise HTTPException(status_code=404,detail="Game Not Found")



