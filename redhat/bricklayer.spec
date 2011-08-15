%define __python python2.6
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary: Builds packages based on git tags or commits 
Name: bricklayer
Version: 1.0
Release: 1
Group: Applications/Databases
License: BSD
URL: http://github.com/locaweb/bricklayer
Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: make, python2.6, python2.6-devel, python-setuptools

Requires: logrotate, python2.6-twisted-core, python-setuptools, python2.6-simplejson, redis
Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig, initscripts
Requires(postun): chkconfig, initscripts

%description
Bricklayer is a twisted application which watches your repository and builds
debian and redhat packages for any change in tags or commits

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
install -p -D -m 0755 init.d %{buildroot}%{_initrddir}/%{name}

sed -i '/^system:/s/: .*/: rpm/g' %{buildroot}%{_sysconfdir}/%{name}/%{name}.ini

find %{buildroot} -type f -iname \*.py[co] -exec rm -f {} \;

%clean
rm -rf %{buildroot}
rm -rf %{_builddir}/%{name}-%{version}

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 = 0 ]; then
   /sbin/service %{name} stop > /dev/null 2>&1
   /sbin/chkconfig --del %{name}
fi

%postun
/sbin/service %{name} condrestart >/dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
%doc doc/* deps.txt MANIFEST.in README.textile
%config %attr(0644, root, root) %{_sysconfdir}/%{name}/*
%{python_sitelib}/%{name}
%{python_sitelib}/%{name}-%{version}-*.egg-info
%{_localstatedir}/lib/%{name}
%{_bindir}/build_consumer
%{_initrddir}/%{name}

%changelog
* Thu Aug 11 2011 Root <root@centos.localdomain> - 1.0-1
- Initial release.
