%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           translate-toolkit
Version:        1.0.1
Release:        2%{?dist}
Summary:        Tools to assist with localization

Group:          Development/Tools
License:        GPL
URL:            http://translate.sourceforge.net/
Source0:        http://downloads.sourceforge.net/translate/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch1:         translate-toolkit-1.0.1-python25.patch

BuildArch:      noarch
BuildRequires:  python-devel
Requires:       python-enchant
Requires:       python-Levenshtein
Requires:       python-psyco

%description
A set of tools for managing localization via Gettext PO or XLIFF format files.

Including:
  * Convertors: convert from various formats to PO or XLIFF
  * Formats:
    * Core localization formats - XLIFF and Gettext PO
    * Other localization formats - TMX, TBX, Qt Linguist (.ts)
    * Other formats - Java .properties, text, HTML, CSV
    * Specialised - OpenOffice.org GSI/SDF, Mozilla (.dtd, .properties, etc)
  * Tools: count, search and debug localization files
  * Checkers: validate translations with over 40 checks


%prep
%setup -q
%patch1 -p1 -b .python25


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
	pocompendium|poen|pomigrate2|popuretext|poreencode|posplit|pocount|poglossary|lookupclient.py)
	  ;;
	*)
		LC_ALL=C PYTHONPATH=. $program --manpage \
		>  $RPM_BUILD_ROOT/%{_mandir}/man1/$(basename $program).1 \
		|| rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/$(basename $program).1
	  ;;
	esac
done

# We will take docs from the tarball
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/doc
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/COPYING
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/ChangeLog
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/LICENSE
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/README
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/convert/TODO
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/filters/TODO
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/misc/README
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/translate/tools/TODO



%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc translate/doc/user/toolkit-[a-z]*
%doc translate/ChangeLog translate/COPYING translate/README
%dir %{python_sitelib}/translate
%dir %{python_sitelib}/translate/tools
%dir %{python_sitelib}/translate/filters
%dir %{python_sitelib}/translate/storage
%dir %{python_sitelib}/translate/misc
%dir %{python_sitelib}/translate/convert
%{python_sitelib}/translate/*.py*
%{python_sitelib}/translate/*/*.py*
%{_bindir}/*
%{_mandir}/*
%exclude %{_bindir}/*.pyc
%exclude %{_bindir}/*.pyo


%changelog
* Thu Dec 20 2007 Dwayne Bailey <dwayne@translate.org.za> - 1.0.1-2
- Create man pages

* Thu Dec 19 2007 Dwayne Bailey <dwayne@translate.org.za> - 1.0.1-1
- Update to upstream 1.0.1
- Update patch for Python 2.5 ElementTree
- Cleanup the doc installation

* Tue Jan 09 2007 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.10.1-4
- Patch to use Python 2.5's built-in ElementTree

* Sat Dec 30 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.10.1-3
- Rebuild to fix dependency problem

* Sat Dec 09 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.10.1-2
- Rebuild for Python 2.5

* Thu Nov 09 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.10.1-1
- Update to upstream 0.10.1
- Cleanup based on latest Python packaging guidelines

* Wed Nov 08 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-2
- Rebuild to get into Rawhide

* Mon Feb 20 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-1
- Update to final 0.8

* Sun Feb 19 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.10.rc6
- Fix a typo in po2dtd that made po2moz fail

* Tue Feb 14 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.9.rc6
- Rebuild for Fedora Extras 5

* Tue Feb 07 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.8.rc6
- Require python-enchant for spellchecking support in pofilter

* Sat Feb 04 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.7.rc6
- Rebuild

* Sat Feb 04 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.6.rc6
- Update to 0.8rc6

* Sat Jan 21 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.5.rc5
- Use sed instead of dos2unix

* Mon Jan 09 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.4.rc5
- Own forgotten subdirectories

* Mon Jan 09 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.3.rc5
- Fix the jToolkit requirement

* Sun Jan 08 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.2.rc5
- Add %%{?dist} tag

* Sat Jan 07 2006 Roozbeh Pournader <roozbeh@farsiweb.info> - 0.8-0.1.rc5
- Initial packaging
