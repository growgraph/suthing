from suthing.connection.factory import ConfigFactory


def test_factory():
    arango_args = {
        "protocol": "http",
        "hostname": "127.0.0.1",
        "port": 8529,
        "cred_name": "root",
        "cred_pass": "123",
        "database": "root",
        "db_type": "arango",
    }
    ac = ConfigFactory.create_config(arango_args)
    assert int(ac.port) == 8529
    assert ac.url[-4:] == str(ac.port)


def test_wsgi():
    args = {
        "db_type": "wsgi",
        "protocol": "http",
        "hostname": "127.0.0.1",
        "port": 8529,
        "path": "/re",
    }
    ac = ConfigFactory.create_config(args)
    assert ac.url[-2:] == "re"


def test_wsgi_hosts():
    args = {
        "db_type": "wsgi",
        "hosts": "http://192.168.0.1:111/lm/re_v3",
    }
    ac = ConfigFactory.create_config(args)
    assert ac.path[0] == "/"
    assert int(ac.port) == 111


def test_wsgi_hosts2():
    args = {
        "comment": "config for gg demo; parse text; retrieve graph from db",
        "protocol": "https",
        "hostname": "something.io",
        "port": 443,
        "db_type": "wsgi",
    }
    ac = ConfigFactory.create_config(args)
    assert ac.path[0] == "/"
    assert int(ac.port) == 443
