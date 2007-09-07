/*
 Copyright 2007 Zuza Software Foundation
 
 This file is part of translate.

 translate is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.
 
 translate is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with translate; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

%module gettextpo
%{
/* Includes the header in the wrapper code */
#include "gettext-po.h"
%}
/* Rename some functions that are versioned */
%rename(po_file_read) po_file_read_v3;
%rename(po_file_write) po_file_write_v2;
%rename(po_message_check_format) po_message_check_format_v2;

%ignore _GETTEXT_PO_H;
%feature("autodoc", "1"); // Document functions

/* Parse the header file to generate wrappers */
%include "gettext-po.h"
