%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define         fullname Pootle

Name:           pootle
Version:        2.0.0
Release:        1%{?dist}
Summary:        Localization and translation management web application

Group:          Development/Tools
License:        GPLv2+
URL:            http://translate.sourceforge.net/wiki/pootle/index
Source:         http://downloads.sourceforge.net/project/translate/%{fullname}/%{version}/%{fullname}-%{version}.tar.bz2
Source1:        pootle.conf
Source2:        README.fedora
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch0:         pootle-2.0.0-rc2-fedora-settings.patch

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  translate-toolkit >= 1.4.1
Requires:       Django >= 1.0
Requires:       iso-codes
Requires:       memcached
Requires:       mod_wsgi
Requires:       python-lxml
Requires:       python-memcached
Requires:       python-Levenshtein
Requires:       translate-toolkit >= 1.5.1
Requires:       xapian-bindings-python >= 1.0.13
Requires:       xapian-core
Requires:       zip
# This is for /sbin/service
Requires(post): initscripts
Requires(postun): initscripts



%description
Pootle is web application for managing distributed or crowdsourced
translation.

It's features include::
  * Translation of Gettext PO and XLIFF files.
  * Submitting to remote version control systems (VCS).
  * Managing groups of translators
  * Online webbased or offline translation
  * Quality checks


%prep
%setup -q -n %{fullname}-%{version}
%patch0 -p1 -b .fedora-settings


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# Create the manpages
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man1
for program in $RPM_BUILD_ROOT/%{_bindir}/*;
do
    case $(basename $program) in
    PootleServer|import_pootle_prefs)
        ;;
    *)
        LC_ALL=C PYTHONPATH=. $program --manpage \
        >  $RPM_BUILD_ROOT/%{_mandir}/man1/$(basename $program).1 \
        || rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/$(basename $program).1
        ;;
    esac
done

install -d $RPM_BUILD_ROOT/usr/sbin $RPM_BUILD_ROOT/usr/share/pootle/ $RPM_BUILD_ROOT/var/lib/pootle $RPM_BUILD_ROOT/etc/pootle
install $RPM_BUILD_ROOT/usr/bin/PootleServer $RPM_BUILD_ROOT/usr/sbin
rm $RPM_BUILD_ROOT/usr/bin/PootleServer
install -p --mode=644 %{SOURCE1} -D $RPM_BUILD_ROOT/etc/httpd/conf.d/pootle.conf
install wsgi.py $RPM_BUILD_ROOT/usr/share/pootle/
cp -p %{SOURCE2} .


%clean
rm -rf $RPM_BUILD_ROOT


%post
/sbin/service httpd restart >/dev/null 2>&1 || :
/sbin/service memcached restart >/dev/null 2>&1 || :


%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service httpd condrestart >/dev/null 2>&1 || :
    /sbin/service memcached condrestart >/dev/null 2>&1 || :
fi


%files
%defattr(-,root,root,-)
%doc COPYING ChangeLog README README.fedora
%{_bindir}/*
%{_sbindir}/*
%{_mandir}/man1/*
%config(noreplace) /etc/pootle
%config(noreplace) /etc/httpd/conf.d/pootle.conf
%{python_sitelib}/*
/usr/share/pootle
%attr(-,apache,apache) /var/lib/pootle
%exclude /usr/share/doc/pootle


%changelog
* Mon Dec 7 2009 Dwayne Bailey <dwayne@translate.org.za> - 2.0.0-1
- Update to 2.0.0 final
- Prefer running under Apache and drop standalone supporting infrastructure

* Fri Nov 27 2009 Dwayne Bailey <dwayne@translate.org.za> - 2.0.0-0.1.rc2
- Update to 2.0.0 rc2

* Thu Nov 5 2009 Dwayne Bailey <dwayne@translate.org.za> - 1.3.0-0.3
- Depend on mod_wsgi

* Mon Nov 2 2009 Dwayne Bailey <dwayne@translate.org.za> - 1.3.0-0.2
- Update to 1.3.0 beta4
- Enable mod_wsgi operation: require httpd, default pootle.conf
- Backport DB initialisation
- Add dependencies for performance: memcached, Levenshtein, xapian
- Fedora README

* Thu Jan 8 2009 Dwayne Bailey <dwayne@translate.org.za> - 1.3.0-0.1
- Django based Pootle

* Mon Oct 6 2008 Dwayne Bailey <dwayne@translate.org.za> - 1.2.0-1
- Update to final 1.2.0 release

* Tue Sep 30 2008 Dwayne Bailey <dwayne@translate.org.za> - 1.2.0-0.5.rc1
- Update to RC1

* Tue Sep 2 2008 Dwayne Bailey <dwayne@translate.org.za> - 1.2.0-0.4.beta2
- Create run_pootle.sh wrapper for server

* Wed Aug 27 2008 Dwayne Bailey <dwayne@translate.org.za> - 1.2.0-0.3.beta2
- Create man pages
- Rebuild with a refreshed tarball that contains jquery

* Wed Aug 27 2008 Dwayne Bailey <dwayne@translate.org.za> - 1.2.0-0.2.beta2
- Update to 1.2.0-beta2
- Fix initscript installation location

* Sun Aug 24 2008 Dwayne Bailey <dwayne@translate.org.za> - 1.2.0-0.1.beta1
- Build for 1.2.0-beta1 release
- Create initscripts, sysconfig; create proper logging; configure stats database

* Thu Feb 14 2008 Dwayne Bailey <dwayne@translate.org.za> - 1.0.2-1
- Rebuild for fc9

* Thu Feb 14 2008 Dwayne Bailey <dwayne@translate.org.za> - 1.0.2-1
- Initial packaging
