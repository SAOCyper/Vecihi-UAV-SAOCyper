#include <windows.h>
#include <stdio.h>
#include <winsock2.h>

#pragma comment(lib, "Ws2.lib")

/// Set IP address and port number according to server IP address and port number
#define SERVER_IP_ADDRESS    "10.18.1.105"
#define PORT_NUMBER          23
#define BUFFER_SIZE          255
 
int wmain()
{
    DWORD choice = 0;
    BOOL loopMenu = TRUE;
    WSADATA ws;                ///< Structure to contain information about the Windows Socket implementation
    SOCKET commSocket;
    int retVal = 0;
    char sendBuffer[BUFFER_SIZE] = {0};
    char recvBuffer[BUFFER_SIZE] = {0};
    struct sockaddr_in serverinfo;
 
    retVal = WSAStartup(0x0101, &ws);                              ///< Initialize ws2.dll (library used for socket programming)
    if (retVal != 0)                                               ///< If WSAStartup failed to initialize
    {
        printf("WSAStartup failed with error: %d\n", WSAGetLastError());
        exit(1);
    }
 
    commSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);        ///< Socket creation
    if (commSocket == INVALID_SOCKET)
    {
        printf("\nSocket creation failed with error code : %d", WSAGetLastError());
        WSACleanup();
        exit(1);
    }
 
    /// Socket binding
    serverinfo.sin_family = AF_INET;                                ///< TCP/UDP socket
    serverinfo.sin_addr.s_addr = inet_addr(SERVER_IP_ADDRESS);      ///< IP Address of Server
    serverinfo.sin_port = htons(PORT_NUMBER);                       ///< Port number used for communication
 
    retVal = connect(commSocket, (LPSOCKADDR)&serverinfo, sizeof(struct sockaddr));   ///< Connect to Server
    if (retVal == SOCKET_ERROR)
    {
        printf("\nCould not connect to Server with error code : %d", WSAGetLastError()); 
        WSACleanup();
        return FALSE;
    }
 
    printf("Demo program to send and receive data over LAN, Toradex Module as client\n"); 
    while (loopMenu == TRUE)
    {
        printf("\n1. Send\n2. Receive\n3. Exit\n");
        scanf_s("%d", &choice);
        switch(choice)
        {
        case 1:
            printf("\nSend = ");
            scanf_s("%s", sendBuffer);
            retVal = send(commSocket, sendBuffer, strlen(sendBuffer), 0);
            if (retVal == SOCKET_ERROR)
            {
                printf("\nCould not send message to Server with error code : %d", WSAGetLastError());
            }
            break;
        case 2:
            printf("\nEntering Listen Mode \n");
            retVal = recv(commSocket, recvBuffer, BUFFER_SIZE, 0);  ///< Receive from server
            if (retVal == SOCKET_ERROR)
            {
                printf("\nCould not receive from Server with error code : %d", WSAGetLastError());
            }
            else
            {
                printf("\nMessage received from server : %s", recvBuffer);
                memset(&recvBuffer[0], 0, sizeof(recvBuffer));
            }
            break;
        case 3:
            loopMenu = FALSE;
            break;
        default:
            printf("\nInvalid Choice");
            break;
        }
    }
    closesocket(commSocket);
    WSACleanup();                                                   ///< Releasing ws2.dll
    return TRUE;
}