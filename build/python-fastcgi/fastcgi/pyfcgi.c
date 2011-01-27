/*
 * pyfcgi.c: Python wrapper for the Open Market FastCGI library
 *
 * Copyright (C) 2002 - 2005 Cody Pisto.
 * 
 * Portions copyright the Python Software Foundation.
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
 * MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE AUTHORS AND
 * CONTRIBUTORS ACCEPT NO RESPONSIBILITY IN ANY CONCEIVABLE MANNER.
 *
 *
 * Author: cody@hpcs.com
 *
 *
 * History:
 *
 * March 27, 2002:
 *     Initial release.
 * 
 * October 1, 2005:
 *     Fixed Stream.read behavior to match that
 *     of the builtin file object.
 *     Previously, size was a required parameter,
 *     and any non positive integer size,
 *     resulted in an exception.
 *
 * December 8, 2005:
 *     Implemented remaining methods required
 *     to bring the Stream object into compliance
 *     with the WSGI 1.0 (PEP 333) spec for I/O
 *     streams. (Stream.[readlines|writelines])
 *
 * December 13, 2005:
 *     Compiler warning fix
 *     Python 2.3 compatibility fix
 *
 */

#include <Python.h>
#include "structmember.h"
#include "fcgiapp.h"

/* for Python 2.3 compatibility */
#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None
#endif

/*
 * Type definitions
 */
typedef struct {
    PyObject_HEAD
    FCGX_Stream **s;
} fcgi_Stream;

typedef struct {
    PyObject_HEAD
    PyObject *s_in;
    PyObject *s_out;
    PyObject *s_err;
    PyObject *env;
    FCGX_Request r;
} fcgi_Request;

/*
 * fcgi_Stream methods
 */
#define fcgi_Stream_Check() \
if (self->s == NULL || *(self->s) == NULL) { \
    PyErr_SetString(PyExc_ValueError, "I/O operation on closed file"); \
    return NULL; \
}

/*
 * The read function and supporting code is mostly
 * based on the builtin python file object code, so
 * behavior should be comparable.
 * 
 * see Python's fileobject.c:file_read()
 *
 */

#define BUF(v) PyString_AS_STRING((PyStringObject *)v)

#if BUFSIZ < 8192
#define SMALLCHUNK 8192
#else
#define SMALLCHUNK BUFSIZ
#endif

#if SIZEOF_INT < 4
#define BIGCHUNK  (512 * 32)
#else
#define BIGCHUNK  (512 * 1024)
#endif

static size_t
new_buffersize(size_t currentsize)
{
    if (currentsize > SMALLCHUNK) {
        /*
         * Keep doubling until we reach BIGCHUNK;
         * then keep adding BIGCHUNK.
         */
        if (currentsize <= BIGCHUNK)
            return currentsize + currentsize;
        else
            return currentsize + BIGCHUNK;
    }
    return currentsize + SMALLCHUNK;
}

static PyObject *
fcgi_Stream_read(fcgi_Stream *self, PyObject *args)
{
    FCGX_Stream *s;
    long bytesrequested = -1;
    size_t bytesread, buffersize, chunksize;
    PyObject *v;

    fcgi_Stream_Check();

    s = *(self->s);

    if (!PyArg_ParseTuple(args, "|l:read", &bytesrequested))
        return NULL;

    if (bytesrequested == 0)
        return PyString_FromString("");

    if (bytesrequested < 0)
        buffersize = new_buffersize((size_t)0);
    else
        buffersize = bytesrequested;

    if (buffersize > INT_MAX) {
        PyErr_SetString(PyExc_OverflowError,
          "requested number of bytes is more than a Python string can hold");
        return NULL;
    }

    v = PyString_FromStringAndSize((char *)NULL, buffersize);
    if (v == NULL)
        return NULL;

    bytesread = 0;

    for (;;) {
        Py_BEGIN_ALLOW_THREADS
        chunksize = FCGX_GetStr(BUF(v) + bytesread, buffersize - bytesread, s);
        Py_END_ALLOW_THREADS

        if (chunksize == 0) {
            if (FCGX_HasSeenEOF(s))
                break;
            PyErr_SetString(PyExc_IOError, "Read failed");
            Py_DECREF(v);
            return NULL;
        }

        bytesread += chunksize;
        if (bytesread < buffersize) {
            break;
        }

        if (bytesrequested < 0) {
            buffersize = new_buffersize(buffersize);
            if (_PyString_Resize(&v, buffersize) < 0)
                return NULL;
        } else {
            /* Got what was requested. */
            break;
        }
    }

    if (bytesread != buffersize)
        _PyString_Resize(&v, bytesread);

    return v;
}

/*
 * Internal function to read a line
 * XXX: does not check for a valid stream,
 * the caller is responsible for that!
 *
 * - if bytesrequested is 0, an empty string is returned
 * - if bytesrequested > 0, it is treated as the max
 *   length of the line to return
 * - if bytesrequested < 0, an arbitrary length line
 *   is returned
 *
 */
static PyObject *
get_line(fcgi_Stream *self, long bytesrequested)
{
    FCGX_Stream *s;
    size_t bytesread, buffersize;
    PyObject *v;
    int c, done;

    s = *(self->s);

    if (bytesrequested == 0)
        return PyString_FromString("");

    if (bytesrequested < 0)
        buffersize = new_buffersize((size_t)0);
    else
        buffersize = bytesrequested;

    if (buffersize > INT_MAX) {
        PyErr_SetString(PyExc_OverflowError,
          "requested number of bytes is more than a Python string can hold");
        return NULL;
    }

    v = PyString_FromStringAndSize((char *)NULL, buffersize);
    if (v == NULL)
        return NULL;

    bytesread = 0;
    done = 0;

    for(;;) {
        Py_BEGIN_ALLOW_THREADS
        while (buffersize - bytesread > 0) {
            c = FCGX_GetChar(s);
            if (c == EOF) {
                if (bytesread == 0) {
                    Py_BLOCK_THREADS
                    Py_DECREF(v);
                    return PyString_FromString("");
                } else {
                    done = 1;
                    break;
                }
            }

            *(BUF(v) + bytesread) = (char) c;
            bytesread++;

            if (c == '\n') {
                done = 1;
                break;
            }
        }
        Py_END_ALLOW_THREADS
        if (done)
            break;

        if (bytesrequested < 0) {
            buffersize = new_buffersize(buffersize);
            if (_PyString_Resize(&v, buffersize) < 0)
                return NULL;
        }
    }

    if (bytesread != buffersize)
        _PyString_Resize(&v, bytesread);

    return v;
}

static PyObject *
fcgi_Stream_readline(fcgi_Stream *self, PyObject *args)
{
    long bytesrequested = -1;

    fcgi_Stream_Check();

    if (!PyArg_ParseTuple(args, "|l:readline", &bytesrequested))
        return NULL;

    return get_line(self, bytesrequested);
}

static PyObject *
fcgi_Stream_readlines(fcgi_Stream *self, PyObject *args)
{
    int err;
    long sizehint = 0;
    size_t total = 0;
    PyObject *list;
    PyObject *l;
   
    fcgi_Stream_Check();

    if (!PyArg_ParseTuple(args, "|l:readlines", &sizehint))
        return NULL;

    if ((list = PyList_New(0)) == NULL)
        return NULL;

    for (;;) {
        l = get_line(self, -1);
        if (l == NULL || PyString_GET_SIZE(l) == 0) {
            Py_XDECREF(l);
            break;
        }

        err = PyList_Append(list, l);
        Py_DECREF(l); 
        if (err != 0)
            break;

        total += PyString_GET_SIZE(l);
        if (sizehint && total >= sizehint)
            break;
    }

    return list;
}

static PyObject *
fcgi_Stream_getiter(fcgi_Stream *self)
{
    fcgi_Stream_Check();

    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *
fcgi_Stream_iternext(fcgi_Stream *self)
{
    PyObject *l;

    fcgi_Stream_Check();

    l = get_line(self, -1);
    if (l == NULL || PyString_GET_SIZE(l) == 0) {
        Py_XDECREF(l);
        return NULL;
    }
    return (PyObject *)l;
}

static PyObject *
fcgi_Stream_write(fcgi_Stream *self, PyObject *args)
{
    int wrote;
    FCGX_Stream *s;
    int len;
    char *data;

    fcgi_Stream_Check();

    s = *(self->s);

    if (!PyArg_ParseTuple(args, "s#", &data, &len))
        return NULL;

    if (len == 0) {
        Py_RETURN_NONE;
    }

    Py_BEGIN_ALLOW_THREADS
    wrote = FCGX_PutStr(data, len, s);
    Py_END_ALLOW_THREADS

    if (wrote < len) {
        if (wrote < 0) {
            PyErr_SetString(PyExc_IOError, "Write failed");
        } else {
            char msgbuf[256];
            PyOS_snprintf(msgbuf, sizeof(msgbuf),
                  "Write failed, wrote %d of %d bytes",
                  wrote, len);
            PyErr_SetString(PyExc_IOError, msgbuf);
        }
        return NULL;
    }

    Py_RETURN_NONE;
}

/* This is a hacked version of Python's fileobject.c:file_writelines(). */
static PyObject *
fcgi_Stream_writelines(fcgi_Stream *self, PyObject *seq)
{
#define CHUNKSIZE 1000
    FCGX_Stream *s;
    PyObject *list, *line;
    PyObject *it;   /* iter(seq) */
    PyObject *result;
    int i, j, index, len, nwritten, islist;

    fcgi_Stream_Check();

    s = *(self->s);

    result = NULL;
    list = NULL;
    islist = PyList_Check(seq);
    if  (islist)
        it = NULL;
    else {
        it = PyObject_GetIter(seq);
        if (it == NULL) {
            PyErr_SetString(PyExc_TypeError,
                "writelines() requires an iterable argument");
            return NULL;
        }
        /* From here on, fail by going to error, to reclaim "it". */
        list = PyList_New(CHUNKSIZE);
        if (list == NULL)
            goto error;
    }

    /* Strategy: slurp CHUNKSIZE lines into a private list,
       checking that they are all strings, then write that list
       without holding the interpreter lock, then come back for more. */
    for (index = 0; ; index += CHUNKSIZE) {
        if (islist) {
            Py_XDECREF(list);
            list = PyList_GetSlice(seq, index, index+CHUNKSIZE);
            if (list == NULL)
                goto error;
            j = PyList_GET_SIZE(list);
        }
        else {
            for (j = 0; j < CHUNKSIZE; j++) {
                line = PyIter_Next(it);
                if (line == NULL) {
                    if (PyErr_Occurred())
                        goto error;
                    break;
                }
                PyList_SetItem(list, j, line);
            }
        }
        if (j == 0)
            break;

        /* Check that all entries are indeed strings. If not,
           apply the same rules as for file.write() and
           convert the results to strings. This is slow, but
           seems to be the only way since all conversion APIs
           could potentially execute Python code. */
        for (i = 0; i < j; i++) {
            PyObject *v = PyList_GET_ITEM(list, i);
            if (!PyString_Check(v)) {
                    const char *buffer;
                    int len;
                if (PyObject_AsReadBuffer(v,
                          (const void**)&buffer,
                                &len) ||
                     PyObject_AsCharBuffer(v,
                               &buffer,
                               &len)) {
                    PyErr_SetString(PyExc_TypeError,
            "writelines() argument must be a sequence of strings");
                    goto error;
                }
                line = PyString_FromStringAndSize(buffer,
                                  len);
                if (line == NULL)
                    goto error;
                Py_DECREF(v);
                PyList_SET_ITEM(list, i, line);
            }
        }

        /* Since we are releasing the global lock, the
           following code may *not* execute Python code. */
        Py_BEGIN_ALLOW_THREADS
        errno = 0;
        for (i = 0; i < j; i++) {
                line = PyList_GET_ITEM(list, i);
            len = PyString_GET_SIZE(line);
            nwritten = FCGX_PutStr(PyString_AS_STRING(line), len, s);
            if (nwritten != len) {
                Py_BLOCK_THREADS
                if (nwritten < 0) {
                    PyErr_SetString(PyExc_IOError, "Write failed");
                } else {
                    char msgbuf[256];
                    PyOS_snprintf(msgbuf, sizeof(msgbuf),
                          "Write failed, wrote %d of %d bytes",
                          nwritten, len);
                    PyErr_SetString(PyExc_IOError, msgbuf);
                }
                goto error;
            }
        }
        Py_END_ALLOW_THREADS

        if (j < CHUNKSIZE)
            break;
    }

    Py_INCREF(Py_None);
    result = Py_None;
  error:
    Py_XDECREF(list);
    Py_XDECREF(it);
    return result;
#undef CHUNKSIZE
}

static PyObject *
fcgi_Stream_flush(fcgi_Stream *self)
{
    int rc;
    FCGX_Stream *s;

    fcgi_Stream_Check();

    s = *(self->s);

    Py_BEGIN_ALLOW_THREADS
    rc = FCGX_FFlush(s);
    Py_END_ALLOW_THREADS

    if (rc == -1) {
        PyErr_SetString(PyExc_IOError, "Flush failed");
        return NULL;
    }

    Py_RETURN_NONE;
}

static void
fcgi_Stream_dealloc(fcgi_Stream *self)
{
    self->ob_type->tp_free((PyObject*)self);
}

#define fcgi_Stream_zero(_s) \
if (_s != NULL) { \
    _s->s = NULL; \
}

static PyObject *
fcgi_Stream_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    fcgi_Stream *self;

    self = (fcgi_Stream *)type->tp_alloc(type, 0);
    fcgi_Stream_zero(self);
    return (PyObject *)self;
}


/*
 * fcgi_Stream setup
 */
static PyMemberDef fcgi_Stream_members[] = {
    {NULL} /* Sentinel */
};

static PyMethodDef fcgi_Stream_methods[] = {
    {"read", (PyCFunction)fcgi_Stream_read, METH_VARARGS,
     "read([size]) -> read at most size bytes, returned as a string."
    },
    {"readline", (PyCFunction)fcgi_Stream_readline, METH_VARARGS,
     "readline([size]) -> next line from the stream, as a string."
    },
    {"readlines", (PyCFunction)fcgi_Stream_readlines, METH_VARARGS,
     "readlines([size]) -> list of strings, each a line from the stream."
    },
    {"write", (PyCFunction)fcgi_Stream_write, METH_VARARGS,
     "write(str) -> None. Write string str to stream."
    },
    {"writelines", (PyCFunction)fcgi_Stream_writelines, METH_O,
     "writelines(sequence_of_strings) -> None.  Write the strings to the stream."
    },
    {"flush", (PyCFunction)fcgi_Stream_flush, METH_NOARGS,
     "flush() -> None. Flush the internal I/O buffer."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject fcgi_StreamType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "fcgi.Stream" ,            /*tp_name*/
    sizeof(fcgi_Stream),       /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)fcgi_Stream_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "FastCGI I/O Stream object", /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    (getiterfunc)fcgi_Stream_getiter, /* tp_iter */
    (iternextfunc)fcgi_Stream_iternext, /* tp_iternext */
    fcgi_Stream_methods,       /* tp_methods */
    fcgi_Stream_members,       /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    fcgi_Stream_new,           /* tp_new */
};


/*
 * fcgi_Stream C API methods
 */
static PyObject *
fcgi_Stream_New(void)
{
    fcgi_Stream *s = PyObject_NEW(fcgi_Stream, &fcgi_StreamType);
    fcgi_Stream_zero(s);
    return (PyObject *)s;
}



/*
 * fcgi_Request methods
 */
static PyObject *
fcgi_Request_accept(fcgi_Request *self)
{
    int rc;
    char **e;

    Py_BEGIN_ALLOW_THREADS
    rc = FCGX_Accept_r(&self->r);
    Py_END_ALLOW_THREADS

    if (rc < 0) {
        /*
         * FCGX_Accept_r returns (0 - errno) on error,
         * so PyErr_SetFromErrno should work just fine
         */
        PyErr_SetFromErrno(PyExc_IOError);
        return NULL;
    }

    /* clear any existing environment */
    PyDict_Clear(self->env);

    if (self->r.envp == NULL) {
        Py_RETURN_NONE;
    }

    /* fill in the environment */
    for (e = self->r.envp; *e != NULL; e++)
    {
        PyObject *k, *v;
        char *p = strchr(*e, '=');
        if (p == NULL)
            continue;
        k = PyString_FromStringAndSize(*e, (int)(p-*e));
        if (k == NULL) {
            PyErr_Clear();
            continue;
        }
        v = PyString_FromString(p + 1);
        if (v == NULL) {
            PyErr_Clear();
            Py_DECREF(k);
            continue;
        }

        if (PyDict_SetItem(self->env, k, v) != 0)
            PyErr_Clear();

        Py_DECREF(k);
        Py_DECREF(v);
    }

    Py_RETURN_NONE;
}

static PyObject *
fcgi_Request_finish(fcgi_Request *self)
{
    Py_BEGIN_ALLOW_THREADS
    FCGX_Finish_r(&self->r);
    Py_END_ALLOW_THREADS

    Py_RETURN_NONE;
}


/* we set the streams internal
 * FCGX_Stream reference to NULL
 * in case anything else is holding
 * a reference to it
 */
#define close_stream(_s) \
if (_s != NULL) { \
    ((fcgi_Stream *)_s)->s = NULL; \
    Py_DECREF(_s); \
}

static void
fcgi_Request_dealloc(fcgi_Request *self)
{
    /* these can be NULL, a fcgi_Stream instance,
     * this macro covers all the bases
     */
    close_stream(self->s_in);
    close_stream(self->s_out);
    close_stream(self->s_err);

    Py_XDECREF(self->env);

    Py_BEGIN_ALLOW_THREADS
    FCGX_Finish_r(&self->r);
    Py_END_ALLOW_THREADS

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
fcgi_Request_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    fcgi_Request *self;

    self = (fcgi_Request *)type->tp_alloc(type, 0);
    if (self != NULL) {
        /* zero out the usual suspects */
        self->s_in = NULL;
        self->s_out = NULL;
        self->s_err = NULL;
        self->env = NULL;

        /* we make sure to zero out
         * the request structure here
         * in case fcgi_Request_init fails
         * so the subsequent FCGX_Finish_r
         * in fcgi_Request_dealloc will
         * behave as expected
         */
        /* initialize fastcgi request */
        FCGX_InitRequest(&self->r, 0, 0);
    }

    return (PyObject *)self;
}

static int 
fcgi_Request_init(fcgi_Request *self, PyObject *args, PyObject *kwds)
{
    /* create streams */
    self->s_in = fcgi_Stream_New();
    if (self->s_in == NULL)
        return -1;

    self->s_out = fcgi_Stream_New();
    if (self->s_out == NULL)
        return -1;

    self->s_err = fcgi_Stream_New();
    if (self->s_err == NULL)
        return -1;

    /* create environment */
    self->env = PyDict_New();
    if (self->env == NULL)
        return -1;

    /* setup streams */
    ((fcgi_Stream *)self->s_in)->s = &(self->r.in);
    ((fcgi_Stream *)self->s_out)->s = &(self->r.out);
    ((fcgi_Stream *)self->s_err)->s = &(self->r.err);

    return 0;
}

/*
 * fcgi_Request setup
 */
static PyMemberDef fcgi_Request_members[] = {
    {"stdin",   T_OBJECT_EX, offsetof(fcgi_Request, s_in),   READONLY, "Standard Input"},
    {"stdout",  T_OBJECT_EX, offsetof(fcgi_Request, s_out),  READONLY, "Standard Output"},
    {"stderr",  T_OBJECT_EX, offsetof(fcgi_Request, s_err),  READONLY, "Standard Error"},
    {"environ", T_OBJECT_EX, offsetof(fcgi_Request, env), READONLY, "Environment"},
    {NULL}  /* Sentinel */
};

static PyMethodDef fcgi_Request_methods[] = {
    {"accept", (PyCFunction)fcgi_Request_accept, METH_NOARGS,
     "Accept a new request"
    },
    {"finish", (PyCFunction)fcgi_Request_finish, METH_NOARGS,
     "Finish a completed request"
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject fcgi_RequestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "fcgi.Request",            /*tp_name*/
    sizeof(fcgi_Request),      /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)fcgi_Request_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "FastCGI Request object",  /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    fcgi_Request_methods,      /* tp_methods */
    fcgi_Request_members,      /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)fcgi_Request_init, /* tp_init */
    0,                         /* tp_alloc */
    fcgi_Request_new,          /* tp_new */
};


/*
 * Module setup
 */
static PyMethodDef fcgi_methods[] = {
    {NULL}  /* Sentinel */
};

PyMODINIT_FUNC
initfcgi(void) 
{
    PyObject* m;

    /* initialize libfcgi */
    FCGX_Init();

    if (PyType_Ready(&fcgi_StreamType) < 0)
        return;
    if (PyType_Ready(&fcgi_RequestType) < 0)
        return;

    m = Py_InitModule3("fcgi", fcgi_methods,
                       "Python wrapper for the Open Market FastCGI library.");

    if (m == NULL)
      return;

    Py_INCREF(&fcgi_StreamType);
    PyModule_AddObject(m, "Stream", (PyObject *)&fcgi_StreamType);

    Py_INCREF(&fcgi_RequestType);
    PyModule_AddObject(m, "Request", (PyObject *)&fcgi_RequestType);
}
