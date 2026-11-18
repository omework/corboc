/* SPDX-License-Identifier: MIT OR Apache-2.0
 * Compile beside target-selected network.c. Exercise its native queue and registry. */
#define main corbo_sample_main
#include "network.c"
#undef main
#include <assert.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
static void await_event(Task *task) {
    struct timespec deadline;clock_gettime(CLOCK_REALTIME,&deadline);deadline.tv_sec+=10;
    pthread_mutex_lock(&task_lock);
    while(!task->io_ready)assert(!pthread_cond_timedwait(&task_ready,&task_lock,&deadline));
    pthread_mutex_unlock(&task_lock);
}
int main(void) {
    reserve(global_fixed_budget);
    int pair[2];assert(!socketpair(AF_UNIX,SOCK_STREAM,0,pair));
    assert(fcntl(pair[0],F_SETFL,O_NONBLOCK)==0);assert(fcntl(pair[1],F_SETFL,O_NONBLOCK)==0);
    char bytes[4096]={0};while(write(pair[0],bytes,sizeof bytes)>0){}
    assert(errno==EAGAIN||errno==EWOULDBLOCK);
    Task readers[3]={{0}},writer={0};int64_t status;
    for(unsigned i=0;i<3;i++)assert(!corbo_socket_wait(&readers[i],pair[0],false,&status));
    assert(!corbo_socket_wait(&writer,pair[0],true,&status));
    pthread_mutex_lock(&task_lock);
    assert(socket_interest(writer.io_token)==3);assert(!writer.io_ready);
    pthread_mutex_unlock(&task_lock);
    assert(write(pair[1],"x",1)==1);
    for(unsigned i=0;i<3;i++)await_event(&readers[i]);
    pthread_mutex_lock(&task_lock);assert(!writer.io_ready);pthread_mutex_unlock(&task_lock);
    while(read(pair[1],bytes,sizeof bytes)>0){}
    await_event(&writer);
    for(unsigned i=0;i<3;i++){assert(corbo_socket_wait(&readers[i],pair[0],false,&status));assert(!status);}
    assert(corbo_socket_wait(&writer,pair[0],true,&status)&&!status);
    pthread_mutex_lock(&task_lock);assert(!socket_waiters);pthread_mutex_unlock(&task_lock);
    close(pair[0]);close(pair[1]);region_release();release();puts("native multi-wait registry passed");
}
