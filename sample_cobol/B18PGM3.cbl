       IDENTIFICATION DIVISION.
       PROGRAM-ID. B18PGM3.
      *******************************************
      *        AUTHOR : PRIYA RANJAN KUMAR      *
      *        PROGRAM: MENU SCREEN             *
      *        VERSION: 1.0                     *
      *        DATE   : 28-JUN-2021             *
      *        DESC   : PROGRAM TO SHOW MENU    *
      *                AND GO TO OPTION SCREENS *
      *******************************************
       DATA DIVISION.
      * --------------------------------------- *
       WORKING-STORAGE SECTION.
      *------- INCLUDING SQL HOST VARIABLES ----*
               EXEC SQL
                   INCLUDE PATDCL
               END-EXEC.
               EXEC SQL
                   INCLUDE DOCDCL
               END-EXEC.
               EXEC SQL
                   INCLUDE DONDCL
               END-EXEC.

      *--- INCLUDING SQL COMMUNICATION AREA ----*
               EXEC SQL
                   INCLUDE SQLCA
               END-EXEC.

      *--- DECLAREING CURSORTS -----------------*
               EXEC SQL
               DECLARE CR1 SCROLL CURSOR FOR
               SELECT  PATIENT_ID,
               PATIENT_NAME,
               PATIENT_GENDER,
               PATIENT_CONTACT_NUM
               FROM PATIENT_DETAIL
               END-EXEC.

               EXEC SQL
               DECLARE CR2 SCROLL CURSOR FOR
               SELECT  DOCTOR_ID,
               DOCTOR_NAME,
               DOCTOR_GENDER,
               DOCTOR_CONTACT_NUM
               FROM DOCTOR_DETAIL
               END-EXEC.

               EXEC SQL
               DECLARE CR3 SCROLL CURSOR FOR
               SELECT  DONOR_ID,
               DONOR_NAME,
               DONOR_GENDER,
               DONOR_CONTACT_NUM
               FROM DONOR_DETAIL
               END-EXEC.
       01 WS-DATE-TIME      PIC S9(10) COMP-3.
       01 WS-END-MSG      PIC X(27) VALUE 'PROGRAM ENDED PLEASE CLEAR'.
       01 WS-END-MSG-LEN  PIC S9(4) COMP VALUE 27.

       01 WS-COMMAREA.
         05 WS-REPORT-READ-FLAG PIC 9 VALUE 0.
         05 WS-REPORT-TYPE-FLAG PIC 9 VALUE 0.
         05 WS-CURSOR-FLAG  PIC 9 VALUE 0.

       01 WS-RESP         PIC S9(8) COMP.
       01 WS-POS          PIC S9(4) COMP VALUE 0.
       01 WS-ID-TEMP      PIC X(18).

       01 WS-MAP-DATA.
        05 WS-ID          PIC X(15).
        05 FILLER         PIC X(02) VALUE SPACES.
        05 WS-NAME        PIC X(30).
        05 FILLER         PIC X(02) VALUE SPACES.
        05 WS-GENDER      PIC X(10).
        05 FILLER         PIC X(02) VALUE SPACES.
        05 WS-CONTACT     PIC X(10).

       01 WS-CTR          PIC 9(9) VALUE 1.

      *--------- COPYBOOK ----------------------*
       COPY B18MPS1.
       COPY DFHAID.
       COPY DFHBMSCA.
       LINKAGE SECTION.
       01 DFHCOMMAREA.
         05 LS-REPORT-READ-FLAG PIC 9.
         05 LS-REPORT-TYPE-FLAG PIC 9.
         05 LS-CURSOR-FLAG  PIC 9.
       PROCEDURE DIVISION.
       1000-MAIN.
            MOVE DFHCOMMAREA TO WS-COMMAREA.
            MOVE LOW-VALUES TO MENUO.
            MOVE -1 TO MOPTL.
            EVALUATE EIBCALEN
            WHEN 0
              PERFORM 2000-SEND-MAP-PARA
            WHEN OTHER
              PERFORM 3000-KEY-VALIDATION-PARA
              PERFORM 2000-SEND-MAP-PARA
            END-EVALUATE.
            PERFORM 4100-HALT-PROGRAM-PARA.
      *--------- SEND MAP PARA -----------------*
       2000-SEND-MAP-PARA.
            PERFORM GET-DATE-TIME-PARA.
      *--------- CHECKING WHICH TO SEND --------*
            EVALUATE  WS-REPORT-TYPE-FLAG
            WHEN 4
            EXEC CICS
                 SEND MAP ('PATREPT')
                 MAPSET ('B18MPS1')
                 ERASE
            END-EXEC
            WHEN 5
            EXEC CICS
                 SEND MAP ('DOCREPT')
                 MAPSET ('B18MPS1')
                 ERASE
            END-EXEC
            WHEN 6
            EXEC CICS
                 SEND MAP ('DONREPT')
                 MAPSET ('B18MPS1')
                 ERASE
            END-EXEC
            WHEN OTHER
            EXEC CICS
                 SEND MAP ('MENU')
                 MAPSET ('B18MPS1')
                 CURSOR
                 ERASE
            END-EXEC
            END-EVALUATE.
      *--------- RECEIVE MAP PARA --------------*
       2100-RECEIVE-MAP-PARA.
            EXEC CICS
                 RECEIVE MAP('MENU')
                 MAPSET ('B18MPS1')
                 RESP(WS-RESP)
            END-EXEC.
            EVALUATE WS-RESP
              WHEN DFHRESP(NORMAL)
                   CONTINUE
              WHEN DFHRESP(MAPFAIL)
                   PERFORM 5000-MAP-FAILED-PARA
              WHEN OTHER
                   PERFORM 5100-ERROR-MSG-PARA
            END-EVALUATE.
      *----CHECKING WHICH KEY IS PRESSED -------*
       3000-KEY-VALIDATION-PARA.
            EVALUATE EIBAID
                     WHEN DFHPF2
                       PERFORM 2100-RECEIVE-MAP-PARA
                       PERFORM 3100-CHECK-OPTION-PARA
                     WHEN DFHPF3
                     IF( WS-REPORT-READ-FLAG = 0) THEN
                       PERFORM 4200-PROGRAM-END-MSG
                       PERFORM 4000-END-PROGRAM-PARA
                     ELSE
                       EXEC CICS XCTL
                       PROGRAM('B18PGM3')
                       END-EXEC
                     END-IF
                     WHEN DFHPF12
                       MOVE LOW-VALUES TO MENUO
                       MOVE -1 TO MOPTL
                       PERFORM 2000-SEND-MAP-PARA
                     WHEN DFHPF7
                       IF( WS-REPORT-READ-FLAG = 0)
                         MOVE 'PLEASE SELECT THE REPORT FIRST' TO MMSGO
                       ELSE
                       EVALUATE WS-REPORT-TYPE-FLAG
                       WHEN 4
                       MOVE LOW-VALUES TO PATREPTO
                       MOVE -5 TO WS-POS
                       PERFORM 6000-PATIENT-REPORT-PARA
                       WHEN 5
                       MOVE LOW-VALUES TO PATREPTO
                       MOVE -5 TO WS-POS
                       PERFORM 6100-DOCTOR-REPORT-PARA
                       WHEN 6
                       MOVE LOW-VALUES TO PATREPTO
                       MOVE -5 TO WS-POS
                       PERFORM 6200-DONOR-REPORT-PARA
                       END-EVALUATE
                       END-IF
                     WHEN DFHPF8
                       IF( WS-REPORT-READ-FLAG = 0)
                         MOVE 'PLEASE SELECT THE REPORT FIRST' TO MMSGO
                       ELSE
                       EVALUATE WS-REPORT-TYPE-FLAG
                       WHEN 4
                        MOVE LOW-VALUES TO PATREPTO
                        MOVE 5 TO WS-POS
                        PERFORM 6000-PATIENT-REPORT-PARA
                       WHEN 5
                        MOVE LOW-VALUES TO DOCREPTO
                        MOVE 5 TO WS-POS
                        PERFORM 6100-DOCTOR-REPORT-PARA
                       WHEN 6
                        MOVE LOW-VALUES TO DONREPTO
                        MOVE 5 TO WS-POS
                        PERFORM 6200-DONOR-REPORT-PARA
                       END-EVALUATE
                       END-IF
                     WHEN OTHER
                       MOVE 'INVALID KEY PRESSED' TO MMSGO
            END-EVALUATE.
      *----VALIDATING INPUT OPTION  ------------*
       3100-CHECK-OPTION-PARA.
            EVALUATE MOPTI
              WHEN 1
                EXEC CICS XCTL
                    PROGRAM('B18PGM4')
                END-EXEC
              WHEN 2
                EXEC CICS XCTL
                    PROGRAM('B18PGM5')
                END-EXEC
              WHEN 3
                EXEC CICS XCTL
                    PROGRAM('B18PGM6')
                END-EXEC
              WHEN 4
                MOVE 1 TO WS-REPORT-READ-FLAG
                MOVE 4 TO WS-REPORT-TYPE-FLAG
                MOVE LOW-VALUES TO PATREPTO
                PERFORM 6000-PATIENT-REPORT-PARA
              WHEN 5
                MOVE 1 TO WS-REPORT-READ-FLAG
                MOVE 5 TO WS-REPORT-TYPE-FLAG
                MOVE LOW-VALUES TO DOCREPTO
                PERFORM 6100-DOCTOR-REPORT-PARA
              WHEN 6
                MOVE 1 TO WS-REPORT-READ-FLAG
                MOVE 6 TO WS-REPORT-TYPE-FLAG
                MOVE LOW-VALUES TO DONREPTO
                PERFORM 6200-DONOR-REPORT-PARA
              WHEN LOW-VALUES
                MOVE 'OPTION CANNOT BE BLANK' TO MMSGO
              WHEN SPACES
                MOVE 'OPTION CANNOT BE BLANK' TO MMSGO
              WHEN OTHER
                MOVE 'ENTER A VALID OPTION'   TO MMSGO
            END-EVALUATE.
      *----------- END PROGRAM PARA ------------*
       4000-END-PROGRAM-PARA.
            EXEC CICS
                RETURN
            END-EXEC.

      *----------- HALTING PROGRAM PARA --------*
       4100-HALT-PROGRAM-PARA.
            EXEC CICS
                RETURN TRANSID('B183')
                COMMAREA(WS-COMMAREA)
            END-EXEC.
      *----------- END PROGRAM MESSAGE PARA ----*
       4200-PROGRAM-END-MSG.
           EXEC CICS
                SEND FROM(WS-END-MSG)
                     LENGTH(WS-END-MSG-LEN)
                     ERASE
           END-EXEC.
       GET-DATE-TIME-PARA.
           EXEC CICS
                ASKTIME
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
           EXEC CICS
                FORMATTIME
                DDMMYYYY(MDATEO)
                DATESEP('/')
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
      *--------- PATIENT CURSOR PARA -----------*
       6000-PATIENT-REPORT-PARA.
             PERFORM OPEN-PATIENT-CURSOR.
             IF( WS-CURSOR-FLAG = 0) THEN
              PERFORM FETCH-PATIENT-PARA 5 TIMES
              ADD 1 TO WS-CURSOR-FLAG
             ELSE
             IF( WS-POS > 0)
               PERFORM SKIP-PATIENT-PARA WS-CURSOR-FLAG TIMES
               IF ( SQLCODE NOT = 100)
               ADD 1 TO WS-CURSOR-FLAG
               END-IF
               PERFORM FETCH-PATIENT-PARA 5 TIMES
             ELSE
               MOVE 5 TO WS-POS
               SUBTRACT 1 FROM WS-CURSOR-FLAG
               PERFORM SKIP-PATIENT-PARA WS-CURSOR-FLAG TIMES
               PERFORM FETCH-PATIENT-PARA 5 TIMES
             END-IF.
             PERFORM CLOSE-PATIENT-CURSOR.
       SKIP-PATIENT-PARA.
                EXEC SQL
                FETCH RELATIVE :WS-POS CR1
                INTO
                :DB-PATIENT-ID,
                :DB-PATIENT-NAME,
                :DB-PATIENT-GENDER,
                :DB-PATIENT-CONTACT-NUM
                END-EXEC.
       FETCH-PATIENT-PARA.
                 EXEC SQL
                     FETCH CR1
                     INTO
                     :DB-PATIENT-ID,
                     :DB-PATIENT-NAME,
                     :DB-PATIENT-GENDER,
                     :DB-PATIENT-CONTACT-NUM
                 END-EXEC.
                 EVALUATE SQLCODE
                 WHEN 0
                 MOVE DB-PATIENT-ID TO  WS-ID-TEMP
                 MOVE WS-ID-TEMP(4:) TO WS-ID
                 MOVE DB-PATIENT-NAME TO  WS-NAME
                 MOVE DB-PATIENT-GENDER TO  WS-GENDER
                 MOVE DB-PATIENT-CONTACT-NUM TO  WS-CONTACT
                 MOVE WS-MAP-DATA TO PATLINEO(WS-CTR)
                 ADD 1 TO WS-CTR
                 WHEN 100
                 MOVE 'END OF RECORD' TO PATREPMO
                 WHEN OTHER
                 MOVE 'ERROR WHILE READING DATA' TO PATREPMO
                 END-EVALUATE.

       OPEN-PATIENT-CURSOR.
                 EXEC SQL
                 OPEN CR1
                 END-EXEC.
       CLOSE-PATIENT-CURSOR.
                 EXEC SQL
                     CLOSE CR1
                 END-EXEC.
      *--------- DOCTOR CURSOR PARA -----------*
       6100-DOCTOR-REPORT-PARA.
             PERFORM OPEN-DOCTOR-CURSOR.
             IF( WS-CURSOR-FLAG = 0) THEN
              PERFORM FETCH-DOCTOR-PARA 5 TIMES
              ADD 1 TO WS-CURSOR-FLAG
             ELSE
             IF( WS-POS > 0)
               PERFORM SKIP-DOCTOR-PARA WS-CURSOR-FLAG TIMES
               IF ( SQLCODE NOT = 100)
               ADD 1 TO WS-CURSOR-FLAG
               END-IF
               PERFORM FETCH-DOCTOR-PARA 5 TIMES
             ELSE
               MOVE 5 TO WS-POS
               SUBTRACT 1 FROM WS-CURSOR-FLAG
               PERFORM SKIP-DOCTOR-PARA WS-CURSOR-FLAG TIMES
               PERFORM FETCH-DOCTOR-PARA 5 TIMES
             END-IF.
             PERFORM CLOSE-DOCTOR-CURSOR.
       SKIP-DOCTOR-PARA.
                EXEC SQL
                FETCH RELATIVE :WS-POS CR2
                INTO
                :DB-DOCTOR-ID,
                :DB-DOCTOR-NAME,
                :DB-DOCTOR-GENDER,
                :DB-DOCTOR-CONTACT-NUM
                END-EXEC.
       FETCH-DOCTOR-PARA.
                 EXEC SQL
                     FETCH CR2
                     INTO
                     :DB-DOCTOR-ID,
                     :DB-DOCTOR-NAME,
                     :DB-DOCTOR-GENDER,
                     :DB-DOCTOR-CONTACT-NUM
                 END-EXEC.
                 EVALUATE SQLCODE
                 WHEN 0
                 MOVE DB-DOCTOR-ID TO   WS-ID-TEMP
                 MOVE WS-ID-TEMP(4:) TO WS-ID
                 MOVE DB-DOCTOR-NAME TO   WS-NAME
                 MOVE DB-DOCTOR-GENDER TO   WS-GENDER
                 MOVE DB-DOCTOR-CONTACT-NUM TO   WS-CONTACT
                 MOVE WS-MAP-DATA TO DOCLINEO(WS-CTR)
                 ADD 1 TO WS-CTR
                 WHEN 100
                 MOVE 'END OF RECORD' TO DOCREPMO
                 WHEN OTHER
                 MOVE 'ERROR WHILE READING DATA' TO DOCREPMO
                 END-EVALUATE.
       OPEN-DOCTOR-CURSOR.
                 EXEC SQL
                 OPEN CR2
                 END-EXEC.
       CLOSE-DOCTOR-CURSOR.
                 EXEC SQL
                     CLOSE CR2
                 END-EXEC.
      *--------- DONOR CURSOR PARA ------------*
       6200-DONOR-REPORT-PARA.
             PERFORM OPEN-DONOR-CURSOR.
             IF( WS-CURSOR-FLAG = 0) THEN
              PERFORM FETCH-DONOR-PARA 5 TIMES
              ADD 1 TO WS-CURSOR-FLAG
             ELSE
             IF( WS-POS > 0)
               PERFORM SKIP-DONOR-PARA WS-CURSOR-FLAG TIMES
              IF ( SQLCODE NOT = 100)
               ADD 1 TO WS-CURSOR-FLAG
              END-IF
               PERFORM FETCH-DONOR-PARA 5 TIMES
             ELSE
               MOVE 5 TO WS-POS
               SUBTRACT 1 FROM WS-CURSOR-FLAG
               PERFORM SKIP-DONOR-PARA WS-CURSOR-FLAG TIMES
               PERFORM FETCH-DONOR-PARA 5 TIMES
             END-IF.
             PERFORM CLOSE-DONOR-CURSOR.
       SKIP-DONOR-PARA.
                EXEC SQL
                FETCH RELATIVE :WS-POS CR3
                INTO
                :DB-DONOR-ID,
                :DB-DONOR-NAME,
                :DB-DONOR-GENDER,
                :DB-DONOR-CONTACT-NUM
                END-EXEC.
       FETCH-DONOR-PARA.
                 EXEC SQL
                     FETCH CR3
                     INTO
                     :DB-DONOR-ID,
                     :DB-DONOR-NAME,
                     :DB-DONOR-GENDER,
                     :DB-DONOR-CONTACT-NUM
                 END-EXEC.
                 EVALUATE SQLCODE
                 WHEN 0
                 MOVE DB-DONOR-ID TO    WS-ID-TEMP
                 MOVE WS-ID-TEMP(4:) TO WS-ID
                 MOVE DB-DONOR-NAME TO    WS-NAME
                 MOVE DB-DONOR-GENDER TO    WS-GENDER
                 MOVE DB-DONOR-CONTACT-NUM TO    WS-CONTACT
                 MOVE WS-MAP-DATA TO DONLINEO(WS-CTR)
                 ADD 1 TO WS-CTR
                 WHEN 100
                 MOVE 'END OF RECORD' TO DONREPMO
                 WHEN OTHER
                 MOVE 'ERROR WHILE READING DATA' TO DONREPMO
                 END-EVALUATE.
       OPEN-DONOR-CURSOR.
                 EXEC SQL
                 OPEN CR3
                 END-EXEC.
       CLOSE-DONOR-CURSOR.
                 EXEC SQL
                     CLOSE CR3
                 END-EXEC.
       5000-MAP-FAILED-PARA.
                 MOVE 'SESSION ENDED DUE TO MAPFAIL' TO WS-END-MSG.
                 PERFORM 4200-PROGRAM-END-MSG.
                 PERFORM 4000-END-PROGRAM-PARA.
       5100-ERROR-MSG-PARA.
                 MOVE 'SESSION ENDED DUE TO ERROR' TO WS-END-MSG.
                 PERFORM 4200-PROGRAM-END-MSG.
                 PERFORM 4000-END-PROGRAM-PARA.
