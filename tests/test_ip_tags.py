from pathlib import Path

import pytest

cases_ip_tags = [
    {
        "url": "http://127.0.0.1:5000/ip-tags/192.0.2.9",
        "expected_data": ["123 & abc & XQZ!", "{$(\n a-tag\n)$}"],
    },
    {
        "url": "http://127.0.0.1:5000/ip-tags/192.0.2.20",
        "expected_data": ["{$(\n a-tag\n)$}"],
    },
    {"url": "http://127.0.0.1:5000/ip-tags/192.1.2.20", "expected_data": []},
]

cases_ip_tags_report = [
    {
        "url": "http://127.0.0.1:5000/ip-tags-report/10.0.0.1",
        "expected_data": "\u2665",
    },
    {
        "url": "http://127.0.0.1:5000/ip-tags-report/192.0.2.20",
        "expected_data": "{$(\n a-tag\n)$}",
    },
]


@pytest.mark.parametrize(
    "url, expected_data",
    [(case["url"], case["expected_data"]) for case in cases_ip_tags],
)
def test_get_ip_tags(client, database, sample_data, url, expected_data):
    """
    GIVEN working app with sample data
    WHEN make request to endpoint /ip-tags/ip
    THEN check if status code and Content-type are ok
         and response is correct
    """

    response = client.get(url)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response_data == expected_data


def test_get_ip_tags_invalid_ip(client, database):
    """
    GIVEN working app with sample data
    WHEN make a request with invalid ip address
    THEN check if status code is set on 400 and response is in
         json with apriopriate error message
    """

    invalid_ip = "http://127.0.0.1:5000/ip-tags/10.1.2.3000"
    response = client.get(invalid_ip)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert (
        response_data["error"]
        == "400 Bad Request: Address 10.1.2.3000 does not have IPv4 format"
    )


@pytest.mark.parametrize(
    "url, expected_data",
    [(case["url"], case["expected_data"]) for case in cases_ip_tags_report],
)
def test__get_ip_tags_report(client, database, sample_data, url, expected_data):
    """
    GIVEN working app with sample data
    WHEN make request to endpoint /ip-tags-report/ip
    THEN check if status code and Content-type are ok
         and expected data are included in response data
    """

    response = client.get(url)
    response_data = response.get_data()

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(expected_data, "utf-8") in response_data


# TODO: test__get_ip_tags_report_invalid_ipv4
# TODO: Checking db_commands blueprint
# TODO: Checking errors blueprint
