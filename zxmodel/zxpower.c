#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <inttypes.h>
#include <ctype.h>
#include <dirent.h>

// read write mmio need rebuild kerbel
// CONFIG_STRICT_DEVMEM=n
// CONFIG_DEVMEM=y
// CONFIG_DEVKMEM=y
// read write msr
// sudo modprobe msr

//sbpmu mmio base[31:12] -> bus0 d17f0 rx(be bd bc)
//svid mmio base = sbpmu mmio base + 0x100
const size_t svid_mmio_base = 0xfeb32100;

//#define MYDEBUG
unsigned char read_devmem_byte(size_t memaddr)
{
  unsigned char ret;
  int fd = -1;
  size_t pagesize = 0;
  size_t filesize = 0;
  unsigned char *mapaddr = NULL;
  size_t fdofffset = 0;
  pagesize = getpagesize();
  fd = open("/dev/mem", O_RDWR | O_SYNC);
  if(fd < 0)
  {
      fprintf(stderr,"open /dev/mem fail\n");
      close(fd);
      return 0;
  }
  filesize = lseek(fd, 0, SEEK_END);
  //lseek(fd,0,SEEK_SET);
  fdofffset = memaddr & (~(pagesize-1));
  //printf("offset is %lx\n", fdofffset);
  mapaddr = (unsigned char*)mmap(NULL,pagesize,PROT_READ|PROT_WRITE,MAP_SHARED, fd,fdofffset); //offset is multiple of page size
  if(mapaddr == NULL)
  {
    fprintf(stderr,"mmap fail\n");
    close(fd);
    return 0;
  }
  ret = *(memaddr-fdofffset + mapaddr);
  munmap(mapaddr,pagesize);
  close(fd);
  return ret;
}

unsigned char write_devmem_byte(size_t memaddr, unsigned char data)
{
  unsigned char ret;
  int fd = -1;
  size_t pagesize = 0;
  size_t filesize = 0;
  unsigned char *mapaddr = NULL;
  size_t fdofffset = 0;
  pagesize = getpagesize();
  fd = open("/dev/mem", O_RDWR | O_SYNC);
  if(fd < 0)
  {
      fprintf(stderr,"open /dev/mem fail\n");
      close(fd);
      return 0;
  }
  filesize = lseek(fd, 0, SEEK_END);
  //lseek(fd,0,SEEK_SET);
  fdofffset = memaddr & (~(pagesize-1));
  //printf("offset is %lx\n", fdofffset);
  mapaddr = (unsigned char*)mmap(NULL,pagesize,PROT_READ|PROT_WRITE,MAP_SHARED, fd,fdofffset); //offset is multiple of page size
  if(mapaddr == NULL)
  {
    fprintf(stderr,"mmap fail\n");
    close(fd);
    return 0;
  }
  *(memaddr-fdofffset + mapaddr) = data;
  munmap(mapaddr,pagesize);
  close(fd);
  return ret;
}

uint64_t rdmsr_on_cpu(uint32_t reg, int cpu)
{
	uint64_t data;
	int fd;
	char *pat;
	int width;
	char msr_file_name[64];
	unsigned int bits;

	sprintf(msr_file_name, "/dev/cpu/%d/msr", cpu);
	fd = open(msr_file_name, O_RDONLY);
	if (fd < 0) 
  {
		fprintf(stderr,"rdmsr open fail\n");
	}

	if (pread(fd, &data, sizeof(data), reg) != sizeof(data)) 
  {
		fprintf(stderr,"rdmsr pread fail\n");
	}
	close(fd);
  return data;
}

/*
* data : hi low  0x288d288d00000000
*/
uint8_t wrmsr_on_cpu(uint32_t reg, int cpu, uint64_t data)
{
  int fd;
  char msr_file_name[64];
  sprintf(msr_file_name,"/dev/cpu/%d/msr",cpu);
  fd = open(msr_file_name,  O_WRONLY | O_SYNC);
  if (fd < 0)
  {
    fprintf(stderr,"wrmsr open fail\n");
    return 1;
  }
  if (pwrite(fd,&data,sizeof(data),reg) != sizeof(data))
  {
    fprintf(stderr,"wrmsr pwrite fail\n");
    return 1;
  }
  close(fd);
  return 0;
}

unsigned char bcdtonum(unsigned char bcd)
{
  unsigned char a,b;
  a = (bcd >> 4);
  b = bcd & 0x0f;
  return (a*10 + b);
}

unsigned char svid_init()
{
  unsigned char rdata, wdata, iccmax_21;
  rdata = read_devmem_byte(svid_mmio_base + 0x08);
  wdata = rdata & 0xdf;  // must diable iout periodically , otherwise random read a error vid 
  //offset 0x08 VRM0 control register
  write_devmem_byte(svid_mmio_base + 0x08, wdata);

  //offset 0x04 VRM0 gerreg reg register ->  which vrm index register
  write_devmem_byte(svid_mmio_base + 0x04, 0x21);
  //offset 0x0b VRM0 command trigger register 
  write_devmem_byte(svid_mmio_base + 0x0b, 0x07);
  //offset 0x05 VRM0 gerreg data register
  iccmax_21 = read_devmem_byte(svid_mmio_base + 0x05);
  #ifdef MYDEBUG
  printf("vrm: icc max is %x\n", iccmax_21);
  #endif
  /*
  rdata = read_devmem_byte(svid_mmio_base + 0x08);
  wdata = rdata | 0x20;
  //offset 0x08 VRM0 control register
  write_devmem_byte(svid_mmio_base + 0x08, wdata); //enable period sample
  write_devmem_byte(svid_mmio_base + 0x0c, 0x10); //time
  */
  return iccmax_21;
}

double giout = 0.0, gv = 0.0;
double vrm_read_power(unsigned char iccmax_21)
{
  unsigned char vid_31, iout_15;
  uint64_t iout_1607;
  double vol = 0, iout = 0, power = 0;

  write_devmem_byte(svid_mmio_base + 0x04, 0x31);
  write_devmem_byte(svid_mmio_base + 0x0b, 0x07);
  vid_31 = read_devmem_byte(svid_mmio_base + 0x05);
  #ifdef MYDEBUG
  printf("vrm: vid is 0x%x\n", vid_31);
  #endif

  vol = 0.25 + (vid_31-1) * 0.005;
  #ifdef MYDEBUG
  printf("vrm: voltage is %f V\n", vol);
  #endif

  write_devmem_byte(svid_mmio_base + 0x04, 0x15);
  write_devmem_byte(svid_mmio_base + 0x0b, 0x07);
  iout_15 = read_devmem_byte(svid_mmio_base + 0x05);
  #ifdef MYDEBUG
  printf("vrm: iid is 0x%x\n", iout_15);
  #endif

  iout_1607 = rdmsr_on_cpu(0x1627,0);
  #ifdef MYDEBUG
  printf("svid: iid from msr 0x1627 is 0x%lx\n",iout_1607);
  #endif

  iout =  2.0 * iout_15 * iccmax_21 / 255.0 ;  //scal is iccmax/(8or6 bit adc)
  giout = iout;
  gv = vol;
  #ifdef MYDEBUG
  printf("vrm: iout is %f A\n", iout);
  #endif

  power = vol * iout;
  #ifdef MYDEBUG
  printf("vrm: power is %f W\n",power);
  #endif
  return power;
}
int main()
{
  unsigned char iccmax = 0;
  double power = 0;
  iccmax = svid_init();
  power = vrm_read_power(iccmax);
  printf("power:%f\n",power);
  return 0;
}
