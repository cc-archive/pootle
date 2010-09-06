%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%global         fullname Pootle

Name:           pootle
Version:        2.1.1
Release:        2%{?dist}
Summary:        Localization and translation management web application

Group:          Development/Tools
License:        GPLv2+
URL:            http://translate.sourceforge.net/wiki/pootle/index
Source:         http://downloads.sourceforge.net/project/translate/%{fullname}/%{version}/%{fullname}-%{version}.tar.bz2
Source1:        pootle.conf
Source2:        README.fedora
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch0:         pootle-2.1.1-1-fedora-settings.patch

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  translate-toolkit >= 1.4.1
Requires:       Django >= 1.0
Requires:       Django-south
%{?fedora:Requires:       iso-codes}
Requires:       memcached
Requires:       mod_wsgi
Requires:       python-djblets
Requires:       python-lxml
Requires:       python-memcached
Requires:       python-Levenshtein
# EL-5 uses Python 2.4 and thus needs sqlite2
%{?rhel:Requires:       python-sqlite2}
Requires:       translate-toolkit >= 1.8.0
%if 0%{?rhel} >= 6 || 0%{?fedora}
Requires:       xapian-bindings-python >= 1.0.13
Requires:       xapian-core
%endif
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

install -d $RPM_BUILD_ROOT%{_sbindir} $RPM_BUILD_ROOT%{_datadir}/pootle/ $RPM_BUILD_ROOT%{_sharedstatedir}/pootle $RPM_BUILD_ROOT%{_sysconfdir}/pootle
install $RPM_BUILD_ROOT%{_bindir}/PootleServer $RPM_BUILD_ROOT%{_sbindir}
rm $RPM_BUILD_ROOT%{_bindir}/PootleServer
rm -r $RPM_BUILD_ROOT%{python_sitelib}/djblets
install -p --mode=644 %{SOURCE1} -D $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/pootle.conf
install wsgi.py $RPM_BUILD_ROOT%{_datadir}/pootle/
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
%config(noreplace) %{_sysconfdir}/pootle
%config(noreplace) %{_sysconfdir}/httpd/conf.d/pootle.conf
%{python_sitelib}/*
%{_datadir}/pootle
%if 0%{?rhel} >= 6 || 0%{?fedora}
%attr(2770,apache,apache) %{_sharedstatedir}/pootle
%else
%attr(2770,apache,apache) /var/lib/pootle
%endif
# We exclude docs as the Pootle installer doesn't do ${name}-${version} as expected in Fedora
%exclude %{_datadir}/doc/pootle


%changelog
* Sat Sep 4 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.1.1-2
- Updated README.fedora with more SELinux information

* Sat Sep 4 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.1.1-1
- Update to 2.1.1
   - Ability to migrate data between different database engines
   - New translations: Slovenian, Songhai, Tamil and Faroese
   - New Apertium API
   - Better caching for imporove performance
     - Save to disk only when there are new translations
     - Cache exported ZIP archives and XLIFF files
   - Fixed a bug where Pootle kept files open even when not needed.
   - Better handling of invalid file types on upload
   - Don't accept empty suggestions
   - HTML registration emails
- Refresh fedora-settings patch

* Fri Sep 3 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.1.0-5
- Set default rights for /var/lib/pootle

* Wed Aug 18 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.1.0-4
- Improve README.fedora to deal with SELinux

* Wed Aug 18 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.1.0-3
- Require Translate Toolkit >= 1.8.0 to fix some multistring issues

* Wed Aug 18 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.1.0-2
- Fix %%if logic for RHEL and Fedora versions

* Wed Aug 18 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.1.0-1
- Update to 2.1.0
   - Improved performance, concurrency and memory consumption
   - UI improvements for translators
   - Machine translation
   - Terminology extraction
   - Formats: Support for monolingual formats without conversion
       - Java properties
       - Mac OSX strings
       - PHP arrays
       - Subtitle files
       - Haiku catkeys
       - Offline translation in XLIFF for all formats
       - Reviewing suggestions offline with the XLIFF alt-trans tag
   - New admin dashboard, contact form
   - Captcha support to combat spam
   - Several new batch operations via the command-line
- Require Django-south for database migration

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 2.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Thu Mar 25 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.0.3-1
- Update to 2.0.3
   - Support for Qt TS files
   - Support for TMX and TBX files
   - Corrections to PostgreSQL support (#1368)
   - Some improvements to memory use
   - Timestamps for news items when viewed on the web
   - It is possible to change tree style more reliably (#1363)
   - More correct method for finding alternative translations
   - A complete translation into Asturian, and other translation updates
- Update to 2.0.2
   - Don't count the templates towards the front page statistics (#1345)
   - Fix password change/reset links work without registration (#1350)
   - Allow deleting translator comments (#1349)
   - Show the date of items on the news page
   - New and updated translations, including Luganda, Punjabi and Asturian
- Remove djblets from external_apps, use the Fedora package instead

* Mon Jan 18 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.0.1-5
- Require python-sqlite2 as its not included in Python 2.4

* Mon Jan 18 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.0.1-4
- Drop Xapian and ISO code support as they're not packaged for EL-5

* Sun Jan 17 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.0.1-3
- Can't use %%{_sharedstatedir}

* Thu Jan 14 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.0.1-2
- Fixes from spec review

* Thu Jan 14 2010 Dwayne Bailey <dwayne@translate.org.za> - 2.0.1-1
- Update to 2.0.1

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
