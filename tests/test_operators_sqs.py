import unittest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
import json

import operators.sqs
import artifacts


class TestSQS(unittest.TestCase):

    @patch('boto3.client')
    def setUp(self, boto3_client):
        self.sqs = operators.sqs.SQS('a', 'b', 'c', 'd')

    def test_process_discards_ip_urls_if_filtered_out(self):
        # control
        self.sqs._sqs_put = Mock()
        self.sqs.filter_string = 'is_domain'
        self.sqs.handle_artifact(artifacts.URL('http://somedomain.com/test', '', ''))
        self.sqs._sqs_put.assert_called_once()

        # test
        self.sqs._sqs_put.reset_mock()
        self.sqs.process([artifacts.URL('http://123.123.123.123/test', '', '')])
        self.sqs._sqs_put.assert_not_called()

    def test_handle_artifact_passes_kwargs_url(self):
        self.sqs._sqs_put = Mock()
        self.sqs.kwargs = {
            'test_arg': 'test_val',
            'test_domain': '{domain}',
            'test_url': '{url}',
        }
        expected_content = json.dumps({
            'test_arg': 'test_val',
            'test_domain': 'somedomain.com',
            'test_url': 'http://somedomain.com/test',
        })
        self.sqs.handle_artifact(artifacts.URL('http://somedomain.com/test', '', ''))
        self.sqs._sqs_put.assert_called_once_with(expected_content)

    def test_handle_artifact_passes_kwargs_hash(self):
        self.sqs._sqs_put = Mock()
        self.sqs.kwargs = {
            'test_arg': 'test_val',
            'test_hash': '{hash}',
        }
        expected_content = json.dumps({
            'test_arg': 'test_val',
            'test_hash': 'test',
        })
        self.sqs.handle_artifact(artifacts.Hash('test', '', ''))
        self.sqs._sqs_put.assert_called_once_with(expected_content)

    def test_handle_artifact_passes_kwargs_ipaddress(self):
        self.sqs._sqs_put = Mock()
        self.sqs.kwargs = {
            'test_arg': 'test_val',
            'test_ipaddress': '{ipaddress}',
        }
        expected_content = json.dumps({
            'test_arg': 'test_val',
            'test_ipaddress': 'test',
        })
        self.sqs.handle_artifact(artifacts.IPAddress('test', '', ''))
        self.sqs._sqs_put.assert_called_once_with(expected_content)

    def test_handle_artifact_passes_kwargs_domain(self):
        self.sqs._sqs_put = Mock()
        self.sqs.kwargs = {
            'test_arg': 'test_val',
            'test_domain': '{domain}',
        }
        expected_content = json.dumps({
            'test_arg': 'test_val',
            'test_domain': 'test',
        })
        self.sqs.handle_artifact(artifacts.Domain('test', '', ''))
        self.sqs._sqs_put.assert_called_once_with(expected_content)

    def test_handle_artifact_passes_kwargs_yarasignature(self):
        self.sqs._sqs_put = Mock()
        self.sqs.kwargs = {
            'test_arg': 'test_val',
            'test_yarasignature': '{yarasignature}',
        }
        expected_content = json.dumps({
            'test_arg': 'test_val',
            'test_yarasignature': 'test',
        })
        self.sqs.handle_artifact(artifacts.YARASignature('test', '', ''))
        self.sqs._sqs_put.assert_called_once_with(expected_content)

    @patch('boto3.client')
    def test_artifact_types_are_set_if_passed_in_else_default(self, boto3_client):
        artifact_types = [artifacts.IPAddress, artifacts.URL]
        self.assertEquals(operators.sqs.SQS('a', 'b', 'c', 'd', artifact_types=artifact_types).artifact_types, artifact_types)
        self.assertEquals(operators.sqs.SQS('a', 'b', 'c', 'd').artifact_types, [artifacts.URL])

    @patch('boto3.client')
    def test_init_sets_config_args(self, boto3_client):
        operator = operators.sqs.SQS('a', 'b', 'c', 'd', filter_string='test', allowed_sources=['test-one'])
        self.assertEquals(operator.filter_string, 'test')
        self.assertEquals(operator.allowed_sources, ['test-one'])
