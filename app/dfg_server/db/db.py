from random import choice, shuffle

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from app.dfg_server.db.exp_submission import exp_is_uuid_private
from app.dfg_server.db.queries import private_images_query, public_images_query, insert_submission, aggregation
from app.dfg_server.db.submission import Submission


class DB:
    transport = RequestsHTTPTransport(url='https://c102-226.cloud.gwdg.de/v1/graphql')
    client = Client(transport=transport, fetch_schema_from_transport=True)

    @staticmethod
    def get_private_images() -> list:
        return DB.client.execute(gql(private_images_query))['private']

    @staticmethod
    def get_public_images() -> list:
        return DB.client.execute(gql(public_images_query))['public']

    @staticmethod
    def get_random_image_set() -> dict:
        """
        completely randomized images from db
        :return [random_100, private_50, public_50]
        """
        private_url = 'https://c102-251.cloud.gwdg.de/private'
        public_url = 'https://c102-251.cloud.gwdg.de/public'
        private_images = DB.get_private_images()
        public_images = DB.get_public_images()

        private = dict()
        public = dict()
        private_count = 0
        while private.__len__() + public.__len__() < 100:
            if private.__len__() < 50:
                c_img = choice(private_images)
                private[c_img['id']] = f"{private_url}/{c_img['filename']}"
                continue
            c_img = choice(public_images)
            public[c_img['id']] = f"{public_url}/{c_img['filename']}"

        result = private | public
        images = list(result.items())
        prv, pub = images[:50], images[50:]
        shuffle(images)
        assert len(images) == 100
        return {
            'random': [{
                'id': v[0],
                'url': v[1]} for v in images],
            'private': [{
                'id': v[0],
                'url': v[1]} for v in prv],
            'public': [{
                'id': v[0],
                'url': v[1]} for v in pub],
        }

    @staticmethod
    def _get_open_submission():
        """
        find submissions between 1 and 40
        """
        doc = DB.client.execute(gql(aggregation))
        # prepare
        private = doc['private']
        private = [{'id': d['id'], 'aggregate': d['submissions_aggregate']['aggregate']['count']} for d in private]
        public = doc['public']
        public = [{'id': d['id'], 'aggregate': d['submissions_aggregate']['aggregate']['count']} for d in public]

        # filter for size
        private = [d for d in private if 1 <= d['aggregate'] <= 40]
        public = [d for d in public if 1 <= d['aggregate'] <= 40]
        return private, public

    @staticmethod
    def get_accumulated_set():
        """
        find images with less than 40 submissions and mix them
        :return:
        """
        private_agg, public_agg = DB._get_open_submission()
        prv_ids = [p['id'] for p in private_agg]
        pub_ids = [p['id'] for p in public_agg]

        prv_agg = [{'id': u, 'url': DB._determine_url(u)} for u in prv_ids]
        pub_agg = [{'id': u, 'url': DB._determine_url(u)} for u in pub_ids]

        randoms = DB.get_random_image_set()
        prv_rdm = randoms['private']
        pub_rdm = randoms['public']

        prv_agg = prv_agg + prv_rdm
        prv_agg = prv_agg[:50]

        pub_agg = pub_agg + pub_rdm
        pub_agg = pub_agg[:50]

        result = prv_agg + pub_agg

        assert len(result) == 100

        shuffle(result)

        return result

    @staticmethod
    def _determine_url(uuid: str):
        private_url = 'https://c102-251.cloud.gwdg.de/private'
        public_url = 'https://c102-251.cloud.gwdg.de/public'
        if exp_is_uuid_private(uuid):
            private_images = DB.get_private_images()
            res = [d['filename'] for d in private_images if d['id'] == uuid].pop()
            return f'{private_url}/{res}'
        public_images = DB.get_public_images()
        res = [d['filename'] for d in public_images if d['id'] == uuid].pop()
        return f'{public_url}/{res}'

    @staticmethod
    def insert_submission(submission: Submission) -> dict:
        submission.check()
        is_private = exp_is_uuid_private(submission.id)
        mutation = gql(insert_submission)
        private_id = None
        public_id = None

        if is_private:
            private_id = submission.id
        else:
            public_id = submission.id

        values = {
            "acquaintance": submission.acquaintance,
            "colleagues": submission.colleagues,
            "family": submission.family,
            "friends": submission.friends,
            "everybody": submission.everybody,
            "nobody": submission.nobody,
            "sensitivity": submission.sensitivity,
            "private_picture": private_id,
            "public_picture": public_id,
            "is_private": is_private,
            "uid": submission.uid
        }
        return DB.client.execute(mutation, variable_values=values)

    @staticmethod
    def add_submission(submission: Submission) -> dict:
        submission.check()
        return DB.insert_submission(submission)
