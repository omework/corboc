/* SPDX-License-Identifier: MIT OR Apache-2.0
 * Deterministic transitions of the production readiness registry. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
typedef struct Task Task;
struct Task {
    Task *root, *io_next;
    uintptr_t io_token;
    uint64_t io_socket;
    int64_t io_error;
    bool io_ready, io_registered, io_write, waiting, parked, blocking;
    unsigned enqueued;
};
static pthread_mutex_t task_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t task_ready = PTHREAD_COND_INITIALIZER;
static void task_enqueue(Task *t) { ++t->enqueued; }
static void *base = (void*)1;
static void reserve(int n) {(void)n;}
static void worker_regions(void) {}
static unsigned last_mask;
static uintptr_t last_token;
static int64_t next_status;
static int64_t corbo_queue_create(void) {return 1;}
static uintptr_t corbo_queue_wait(int64_t q) {(void)q;return 0;}
static int64_t corbo_queue_watch(int64_t q, uint64_t fd, unsigned mask, uintptr_t token) {
    (void)q;(void)fd;last_mask=mask;last_token=token;
    int64_t status=next_status;next_status=0;return status;
}
#include "async/readiness.c.inc"
static void initialized(void) { socket_queue=1;socket_init_error=0; }
static void wait_for(Task *t, uint64_t fd, bool write, bool park) {
    int64_t out=999;
    assert(!corbo_socket_wait(t,fd,write,&out));
    assert(out==999 && t->waiting && t->io_registered);
    if(park)t->parked=true;
}
static void consume(Task *t, int64_t expected) {
    int64_t out=999;
    assert(corbo_socket_wait(t,t->io_socket,t->io_write,&out));
    assert(out==expected && !t->io_registered && !t->io_ready);
}
int main(void) {
    pthread_once(&socket_once,initialized);
    Task a={0},b={0},w={0};
    wait_for(&a,7,false,true);uintptr_t old=a.io_token;
    wait_for(&b,7,false,true);wait_for(&w,7,true,true);
    assert(a.io_token==b.io_token && b.io_token==w.io_token && last_mask==3);
    socket_dispatch(old|2);assert(w.io_ready && w.enqueued==1 && !a.io_ready && !b.io_ready);
    assert(last_mask==1 && socket_waiters && !w.io_next);consume(&w,0);
    socket_dispatch(old|1);assert(a.enqueued==1 && b.enqueued==1 && !socket_waiters && !last_token);
    consume(&a,0);consume(&b,0);
    wait_for(&a,7,false,false);assert(a.io_token!=old);uintptr_t fresh=a.io_token;
    socket_dispatch(old|3);assert(!a.io_ready && a.waiting); /* stale cohort */
    socket_dispatch(fresh|1);assert(a.io_ready && !a.waiting && a.enqueued==1); /* event before park */
    consume(&a,0);
    Task many[12]={0};
    for(unsigned i=0;i<12;i++)wait_for(&many[i],10,i%2,true);
    uintptr_t cohort=many[0].io_token;socket_dispatch(cohort|3);
    for(unsigned i=0;i<12;i++){assert(many[i].enqueued==1);consume(&many[i],0);}
    wait_for(&a,20,false,true);wait_for(&b,21,false,true);
    socket_dispatch(a.io_token|1);assert(!b.io_ready);consume(&a,0);
    socket_dispatch(b.io_token|1);consume(&b,0);
    wait_for(&a,30,false,true);next_status=-77;
    int64_t out=0;assert(corbo_socket_wait(&w,30,true,&out) && out==-77);
    assert(a.io_ready && !socket_waiters);consume(&a,-77); /* registration failure wakes peers */
    wait_for(&a,40,false,true);wait_for(&w,40,true,true);next_status=-88;
    socket_dispatch(a.io_token|1);consume(&a,0);consume(&w,-88); /* rearm failure */
    assert(!socket_waiters);puts("readiness registry passed");
}
