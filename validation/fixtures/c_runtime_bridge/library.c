/* SPDX-License-Identifier: MIT OR Apache-2.0 */
#include "corbo_runtime.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned destroyed;
static void dispose(void *p){assert(*(uint64_t*)p==42);++destroyed;}
int main(void){
 corbo_runtime_init(1024*1024,256*1024,64*1024);
 assert(corbo_runtime_abi_version()==CORBO_RUNTIME_ABI_VERSION);
 CorboStackMark mark=corbo_datastack_mark();
 CorboPool *pool=corbo_pool_create(2,sizeof(uint64_t),2);
 CorboAllocation first=corbo_pool_take(pool,0),second=corbo_pool_take(pool,1);
 *(uint64_t*)corbo_allocation_data(&first)=42;first.destroy=dispose;
 size_t index=first.index;corbo_allocation_drop(&first);corbo_allocation_drop(&first);assert(destroyed==1);
 CorboAllocation reused=corbo_pool_take(pool,0);assert(reused.index==index);
 corbo_allocation_drop(&reused);corbo_allocation_drop(&second);
 CorboRegion region;corbo_region_enter(64*1024,2);corbo_region_new(&region,sizeof(uint64_t),false);
 *(uint64_t*)corbo_region_push(&region)=7;assert(region.len==1&&*(uint64_t*)region.data==7);corbo_region_drop(&region);
 CorboHashMap *map=corbo_map_new(sizeof(uint64_t),0);uint64_t value=19,previous=0;
 assert(!corbo_map_insert(map,7,&value,&previous));assert(*(uint64_t*)corbo_map_get(map,7)==19);
 value=20;assert(corbo_map_insert(map,7,&value,&previous)&&previous==19);
 assert(corbo_map_remove(map,7,&previous)&&previous==20);corbo_map_drop(&map);assert(!map);
 corbo_datastack_rewind(mark);assert(corbo_datastack_info().position==mark.position);corbo_free_pages();
 corbo_runtime_shutdown();puts("C runtime library passed");
}
