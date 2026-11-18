/* SPDX-License-Identifier: MIT OR Apache-2.0
 * Compile beside Windows-selected network.c; exercise distinct outstanding requests. */
#define main corbo_sample_main
#include "network.c"
#undef main
#include <assert.h>
#include <time.h>
static void await_event(Task *task) {
    struct timespec deadline;clock_gettime(CLOCK_REALTIME,&deadline);deadline.tv_sec+=10;
    pthread_mutex_lock(&task_lock);
    while(!task->io_ready)assert(!pthread_cond_timedwait(&task_ready,&task_lock,&deadline));
    pthread_mutex_unlock(&task_lock);
}
int main(void) {
    reserve(global_fixed_budget);
    WSADATA startup;assert(!WSAStartup(MAKEWORD(2,2),&startup));
    SOCKET listener=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);assert(listener!=INVALID_SOCKET);
    struct sockaddr_in address={0};address.sin_family=AF_INET;address.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
    assert(!bind(listener,(void*)&address,sizeof address));assert(!listen(listener,1));int length=sizeof address;
    assert(!getsockname(listener,(void*)&address,&length));
    SOCKET peer=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);assert(!connect(peer,(void*)&address,length));
    SOCKET fd=accept(listener,0,0);assert(fd!=INVALID_SOCKET);assert(!corbo_socket_attach(fd));
    Task tasks[4]={{0}};uint64_t requests[4][25]={{0}};unsigned char bytes[4]={0,0,0,42};int64_t status;
    for(unsigned i=0;i<4;i++){
        requests[i][6]=i==3?2:1;requests[i][7]=1;requests[i][8]=(uintptr_t)&bytes[i];
        assert(!corbo_socket_complete(&tasks[i],fd,(uintptr_t)requests[i],&status));
    }
    char received=0;assert(recv(peer,&received,1,0)==1 && received==42);
    assert(send(peer,"abc",3,0)==3);
    for(unsigned i=0;i<4;i++){
        await_event(&tasks[i]);assert(!requests[i][4]);
        assert(corbo_socket_complete(&tasks[i],fd,(uintptr_t)requests[i],&status)&&!status);
        assert(requests[i][9]==1 && requests[i][10]==0);
    }
    unsigned sum=bytes[0]+bytes[1]+bytes[2];assert(sum=='a'+'b'+'c');
    closesocket(fd);closesocket(peer);closesocket(listener);WSACleanup();region_release();release();
    puts("native IOCP multi-request registry passed");
}
