       IDENTIFICATION DIVISION.
       PROGRAM-ID. B18PGM1.
      *******************************************
      *        AUTHOR : PRIYA RANJAN KUMAR      *
      *        PROGRAM: LOGIN SCREEN            *
      *        VERSION: 1.0                     *
      *        DATE   : 28-JUN-2021             *
      *        DESC   : PROGRAM TO DO LOGIN     *
      *                 PROCESS.                *
      *******************************************
       DATA DIVISION.
      * --------------------------------------- *
       WORKING-STORAGE SECTION.
       01 WS-END-MSG      PIC X(27) VALUE 'PROGRAM ENDED THANK YOU   '.
       01 WS-END-MSG-LEN  PIC S9(4) COMP VALUE 27.

      *----------PESUDO CONVERSION -------------*
       01 WS-COMMAREA.
          05 DUMMY        PIC 9 VALUE 0.

      *----------RECEIVE MAP FLAG  -------------*
       01 WS-RESP         PIC S9(8) COMP.

      *--------- COMMAREA FOR 2ND PGM ----------*
       01 WS-COMMAREA1.
          05 WS-ID       PIC X(06).
          05 WS-PASS     PIC X(06).
          05 WS-FLAG     PIC 9(1) VALUE 0.

       01 WS-DATE-TIME      PIC S9(10) COMP-3.

      *--------- COPYBOOK ----------------------*
       COPY B18MPS1.
       COPY DFHAID.

       PROCEDURE DIVISION.
       1000-MAIN-PARA.
      *--------- CLEAR MAP -------------------- *
            MOVE LOW-VALUES TO LOGINO.
            MOVE -1 TO USERIDL
      *--------- CHECKING FOR EIBCALEN -------- *
            EVALUATE EIBCALEN
              WHEN 0
                   PERFORM 2000-SEND-MAP-PARA
              WHEN OTHER
                   PERFORM 3000-KEY-VALIDATION-PARA
                   PERFORM 2000-SEND-MAP-PARA
            END-EVALUATE.
            PERFORM 4100-HALT-PROGRAM-PARA.
      *--------- SENDING MAP ----------------- *
       2000-SEND-MAP-PARA.
            PERFORM GET-DATE-TIME-PARA.
            EXEC CICS
                SEND MAP('LOGIN')
                     MAPSET('B18MPS1')
                     CURSOR
                     ERASE
            END-EXEC.
      *--------- RECEIVING MAP --------------- *
       2100-RECEIVE-MAP-PARA.
            EXEC CICS
                RECEIVE MAP('LOGIN')
                        MAPSET('B18MPS1')
                        RESP(WS-RESP)
            END-EXEC.
      *--------- HANDELING RESPONSE ---------- *
            EVALUATE WS-RESP
                WHEN DFHRESP(NORMAL)
                    CONTINUE
                WHEN DFHRESP(MAPFAIL)
                    MOVE 'PLEASE ENTER ONLY AFTER ENTERING DATA'
                    TO MSGO
                    PERFORM 2000-SEND-MAP-PARA
                WHEN OTHER
                    MOVE 'MAP IS FAILED, PLEASE OPEN AGAIN' TO MSGO
                    PERFORM 2000-SEND-MAP-PARA
            END-EVALUATE.
      *--- CHECKING WHICH KEY IS PRESSED ----- *
       3000-KEY-VALIDATION-PARA.
            EVALUATE EIBAID
                     WHEN DFHPF2
                       PERFORM 2100-RECEIVE-MAP-PARA
                       PERFORM 3100-CHECK-ID-PASS-PARA
                     WHEN DFHPF3
                       PERFORM 4200-PROGRAM-END-MSG
                       PERFORM 4000-END-PROGRAM-PARA
                     WHEN DFHPF12
                       MOVE LOW-VALUES TO LOGINO
                       MOVE -1 TO USERIDL
                       PERFORM 2000-SEND-MAP-PARA
                     WHEN OTHER
                       MOVE 'INVALID KEY PRESSED' TO MSGO
            END-EVALUATE.
      *--------- VALIDATING INPUT DATA ------- *
       3100-CHECK-ID-PASS-PARA.
            IF NOT ( USERIDI = LOW-VALUES OR USERIDI = SPACES ) THEN
            IF NOT ( PASSWDI = LOW-VALUES OR PASSWDI = SPACES ) THEN
                 MOVE USERIDI TO WS-ID
                 MOVE PASSWDI TO WS-PASS
      *--------- CALLING SUB PROGRAM --------- *
                 EXEC CICS
                 LINK PROGRAM('B18PGM2')
                 COMMAREA(WS-COMMAREA1)
                 END-EXEC
                 EVALUATE WS-FLAG
      *--  CALLING PGM3 IF ID & PASS VALID --- *
                    WHEN 1
                     EXEC CICS XCTL
                     PROGRAM('B18PGM3')
                     END-EXEC
                    WHEN 2
                     MOVE 'WRONG PASSWORD' TO MSGO
                    WHEN 3
                     MOVE 'USER NOT IN REGISTERED' TO MSGO
                 END-EVALUATE
               ELSE
               MOVE 'ALL FIELDS ARE MANDATORY - PLEASE ENTER PASSWORD'
                                             TO MSGO
               MOVE -1 TO USERIDL
               END-IF
            ELSE
               MOVE 'ALL FIELDS ARE MANDATORY - PLEASE ENTER USERID'
                                             TO MSGO
               MOVE -1 TO USERIDL
            END-IF.
      *--------- END PROGRAM ----------------- *
       4000-END-PROGRAM-PARA.
            EXEC CICS
                RETURN
            END-EXEC.

      *--------- HALTING PROGRAM ------------- *
       4100-HALT-PROGRAM-PARA.
            EXEC CICS
                RETURN TRANSID('B181')
                COMMAREA(WS-COMMAREA)
            END-EXEC.
      *--------- PROGRAM END ----------------- *
       4200-PROGRAM-END-MSG.
           EXEC CICS
                SEND FROM(WS-END-MSG)
                     LENGTH(WS-END-MSG-LEN)
                     ERASE
           END-EXEC.
      *------ GETTING DATE FROM SYSTEM ------- *
       GET-DATE-TIME-PARA.
           EXEC CICS
                ASKTIME
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
           EXEC CICS
                FORMATTIME
                DDMMYYYY(DATEO)
                DATESEP('/')
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
