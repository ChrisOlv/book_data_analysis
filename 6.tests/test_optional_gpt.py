import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pandas as pd


SCRIPT = Path(__file__).resolve().parents[1] / '3.transformations/scripts/extract-transform.py'
AZURE_VARIABLES = (
    'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT',
    'AZURE_OPENAI_API_VERSION', 'AZURE_OPENAI_DEPLOYMENT',
)


class AzureHandler(BaseHTTPRequestHandler):
    calls = 0

    def do_POST(self):
        type(self).calls += 1
        self.rfile.read(int(self.headers['Content-Length']))
        if self.calls == 1:
            status = 200
            response = {'choices': [{'message': {'role': 'assistant', 'content': 'fiction/test'}, 'finish_reason': 'stop', 'index': 0}]}
        else:
            status = 401
            response = {'error': {'message': 'Invalid key', 'type': 'invalid_request_error'}}
        body = json.dumps(response).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


class OptionalGptTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.script = self.root / '3.transformations/scripts/extract-transform.py'
        self.script.parent.mkdir(parents=True)
        shutil.copyfile(SCRIPT, self.script)
        self.raw = self.root / '1.data/1.raw/sqlite'
        self.processed = self.root / '1.data/2.processed'
        self.raw.mkdir(parents=True)
        self.processed.mkdir(parents=True)
        (self.root / '1.data/3.archives/sqlite').mkdir(parents=True)

    def create_database(self):
        books = pd.DataFrame([
            {'id': book_id, 'title': f'Book {book_id}', 'authors': 'Test Author',
             'highlights': 0, 'md5': str(book_id), 'series': 'Series #1',
             'language': 'en', 'last_open': 1700000000, 'total_read_pages': 10,
             'pages': 100, 'notes': '', 'total_read_time': 600}
            for book_id in range(1, 4)
        ])
        stats = pd.DataFrame([
            {'id_book': book_id, 'duration': 600, 'start_time': 1700000000}
            for book_id in range(1, 4)
        ])
        with closing(sqlite3.connect(self.raw / 'statistics.sqlite3')) as connection:
            books.to_sql('book', connection, index=False)
            stats.to_sql('page_stat_data', connection, index=False)

    def run_etl(self, settings=None):
        self.create_database()
        env = os.environ.copy()
        for name in AZURE_VARIABLES:
            env.pop(name, None)
        env.update(settings or {})
        return subprocess.run([sys.executable, str(self.script)], env=env, cwd=self.root,
                              capture_output=True, text=True, timeout=60)

    def test_missing_configuration_preserves_cached_values(self):
        result = self.run_etl()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('configuration Azure OpenAI incomplète', result.stdout)
        cached_path = self.processed / 'df_book.parquet'
        books = pd.read_parquet(cached_path)
        self.assertTrue((books['categorie'] == '').all())
        self.assertTrue((books['First published date'] == '').all())
        books.loc[books['id'] == 1, ['categorie', 'First published date']] = ['fiction/test', '2001']
        books.to_parquet(cached_path)

        result = self.run_etl()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        books = pd.read_parquet(cached_path).set_index('id')
        self.assertEqual(books.loc[1, 'categorie'], 'fiction/test')
        self.assertEqual(books.loc[1, 'First published date'], '2001')
        self.assertEqual(books.loc[2, 'categorie'], '')
        self.assertTrue((self.processed / 'df_book_updated.parquet').exists())
        self.assertTrue((self.processed / 'stats_lecture.parquet').exists())

    def test_api_error_stops_enrichment_and_keeps_successes(self):
        AzureHandler.calls = 0
        server = ThreadingHTTPServer(('127.0.0.1', 0), AzureHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)
        result = self.run_etl({
            'AZURE_OPENAI_API_KEY': 'invalid-test-key',
            'AZURE_OPENAI_ENDPOINT': f'http://127.0.0.1:{server.server_port}',
            'AZURE_OPENAI_API_VERSION': '2024-02-01',
            'AZURE_OPENAI_DEPLOYMENT': 'test',
        })
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('erreur API (AuthenticationError)', result.stdout)
        self.assertEqual(AzureHandler.calls, 2)
        books = pd.read_parquet(self.processed / 'df_book.parquet').set_index('id')
        self.assertEqual(books.loc[1, 'categorie'], 'fiction/test')
        self.assertEqual(books.loc[2, 'categorie'], '')
        self.assertEqual(books.loc[3, 'categorie'], '')
        self.assertTrue((books['First published date'] == '').all())


if __name__ == '__main__':
    unittest.main()