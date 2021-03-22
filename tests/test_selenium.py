import timeit


def test_get_ip_tags_50_runs_time(client, selenium):
    """
    GIVEN working production app with sample data
    WHEN make 50 HTTP requests
    THEN execution time should be less than one second
    """

    url1 = "http://0.0.0.0:8000/ip-tags/84.163.160.1"
    url2 = "http://0.0.0.0:8000/ip-tags/177.27.64.1"
    response = client.get(url1)

    if response.status_code == 200:
        start_time = timeit.default_timer()

        for _ in range(25):
            selenium.get(url1)

        for _ in range(25):
            selenium.get(url2)

        execution_time = timeit.default_timer() - start_time

        assert execution_time < 1
