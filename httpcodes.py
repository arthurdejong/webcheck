# Copyright (C) 1998,1999  marduk <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


__version__='0.10'
__author__ = 'Mike Meyer <mwm@miredo.org>'

HTTP_STATUS_CODES= {'100':"Continue",
        	    '101':"Switching Protocols",
        	    '200':"OK",
        	    '201':"Created",
        	    '202':"Accepted",
        	    '204':"No Content",
        	    '205':"Reset Content",
        	    '206':"Partial Content",
        	    '300':"Multiple Choices",
        	    '301':"Moved Permanently",
        	    '302':"Moved Temporarily",
        	    '303':"See Other",
        	    '304':"Not Modified",
        	    '305':"Use Proxy",
        	    '400':"Bad Request",
        	    '401':"Unauthorized",
        	    '402':"Payment Required",
        	    '403':"Forbidden",
        	    '404':"Not Found",
        	    '405':"Method Not Allowed",
        	    '406':"Not Acceptable",
        	    '407':"Proxy Authentication Required",
        	    '408':"Request Time-out",
        	    '409':"Conflict",
        	    '410':"Gone",
        	    '411':"Length Required",
        	    '412':"Precondition Failed",
        	    '413':"Request Entity Too Large",
        	    '414':"Request-URI Too Large",
        	    '415':"Unsupported Media Type",
        	    '500':"Internal Server Error",
        	    '501':"Not Implemented",
        	    '502':"Bad Gateway",
        	    '503':"Service Unavailable",
        	    '504':"Gateway Time-out",
        	    '505':"HTTP Version not supported"
        	    }
