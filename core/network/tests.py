from django.test import TestCase
from django.core.exceptions import ValidationError

from core.network.models import Network
from core.range.models import Range
from mozdns.domain.models import Domain
from mozdns.ip.models import ipv6_to_longs


class NetworkTests(TestCase):

    def do_basic_add(self, network, prefixlen, ip_type, name=None,
                     number=None):
        s = Network(network_str=network + "/" + prefixlen, ip_type=ip_type)
        s.clean()
        s.save()
        self.assertTrue(s)
        return s

    def test1_create_ipv6(self):
        network = "f::"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '6'}
        s = self.do_basic_add(**kwargs)
        str(s)
        s.__repr__()
        self.assertTrue(s)

    def test2_create_ipv6(self):
        network = "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '6'}
        s = self.do_basic_add(**kwargs)
        str(s)
        s.__repr__()
        self.assertTrue(s)
        ip_upper, ip_lower = ipv6_to_longs(network)
        self.assertEqual(s.ip_upper, ip_upper)
        self.assertEqual(s.ip_lower, ip_lower)

    def test_bad_resize(self):
        network = "129.0.0.0"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4'}
        s = self.do_basic_add(**kwargs)
        self.assertTrue(s)

        d = Domain(name="asdf")
        d.save()

        start_str = "129.0.0.1"
        end_str = "129.0.0.255"
        network = s

        r = Range(start_str=start_str, end_str=end_str, network=network)
        r.save()

        self.assertEqual(r.network, s)
        self.assertTrue(len(s.range_set.all()) == 1)

        s.network_str = "129.0.0.0/25"
        self.assertRaises(ValidationError, s.clean)

    def test_bad_delete(self):
        network = "129.0.0.0"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4'}
        s = self.do_basic_add(**kwargs)
        s_pk = s.pk
        self.assertTrue(s)

        d = Domain(name="asdf")
        d.save()

        start_str = "129.0.0.1"
        end_str = "129.0.0.255"
        network = s

        r = Range(start_str=start_str, end_str=end_str, network=network)
        r.clean()
        r.save()

        self.assertEqual(r.network, s)
        self.assertTrue(len(s.range_set.all()) == 1)

        self.assertRaises(ValidationError, s.delete)
        self.assertTrue(Network.objects.get(pk=s_pk))

        r.delete()
        s.delete()
        self.assertEqual(len(Network.objects.filter(pk=s_pk)), 0)
