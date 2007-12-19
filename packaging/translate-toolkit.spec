%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           translate-toolkit
Version:        0.10.1
Release:        4%{?dist}
Summary:        A collection of tools to assist software localization

Group:          Development/Tools
License:        GPL
URL:            http://translate.sourceforge.net/
Source0:        http://dl.sourceforge.net/sourceforge/translate/translate-toolkit-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch1:         translate-toolkit-0.10.1-python25.patch

BuildArch:      noarch
BuildRequires:  python-devel
Requires:       python-enchant

%description
The Translate Toolkit includes programs to convert various localization
formats to the common gettext PO format and vice versa, and programs to
check and manage PO files. Also part of the package are programs to create
word counts, merge translations, and perform various checks on PO files.


%prep
%setup -q
%patch1 -p1 -b .python25


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# This removes the documentation files that were installed in site-packages
find $RPM_BUILD_ROOT%{python_sitelib}/translate -type f -name "[[:upper:]]*" | xargs rm -fv


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
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
%exclude %{_bindir}/*.pyc
%exclude %{_bindir}/*.pyo


%changelog
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
