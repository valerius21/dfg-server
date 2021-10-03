import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from fastapi.middleware.cors import CORSMiddleware

from app.dfg_server.db.db import DB
from app.dfg_server.db.submission import Submission, SubmissionContradictionError

app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=[
                       'https://*.cloud.gwdg.de',
                       'http://localhost:3000',
                       'https://localhost:3000',
                       'https://localhost:443',
                       'https://localhost',
                       'http://localhost:80',
                       'http://localhost',
                       '*'
                   ],
                   allow_methods=['*'],
                   allow_headers=['*'],
                   allow_credentials=True
                   )


@app.get('/')
def redirect_root():
    return RedirectResponse('/docs')


@app.get('/acc')
def accumulated_images():
    return {'images': DB.get_accumulated_set()}


@app.get('/rdm')
def random_images():
    return {'images': DB.get_random_image_set()['random']}


@app.post('/submit')
def submit_image_evaluation(submission: Submission):
    try:
        return DB.insert_submission(submission)
    except SubmissionContradictionError:
        raise HTTPException(status_code=400, detail="Verification failed! (Illegal demography selection)")


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
