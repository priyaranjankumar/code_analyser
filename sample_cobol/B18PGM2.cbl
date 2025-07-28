       IDENTIFICATION DIVISION.
       PROGRAM-ID. B18PGM2.
      *******************************************
      *        AUTHOR : PRIYA RANJAN KUMAR      *
      *        PROGRAM: ID AND PASS VERIFICATON *
      *        VERSION: 1.0                     *
      *        DATE   : 28-JUN-2021             *
      *        DESC   : PROGRAM TO DO ID AND    *
      *                 PASSWORD VERIFICATION   *
      *******************************************
       DATA DIVISION.
      * --------------------------------------- *
       WORKING-STORAGE SECTION.
      *------- INCLUDING SQL HOST VARIABLES ----*
            EXEC SQL
                 INCLUDE USERSDCL
            END-EXEC.

      *--- INCLUDING SQL COMMUNICATION AREA ----*
            EXEC SQL
                 INCLUDE SQLCA
            END-EXEC.
       LINKAGE SECTION.
      *--- RECEIVING DATA FROM PROGRAM 1 -------*
       01 DFHCOMMAREA.
          05 LS-USER-ID    PIC X(06).
          05 LS-USER-PASS  PIC X(06).
          05 LS-VALID-FLAG PIC 9(01).
       PROCEDURE DIVISION.
      *---- CHECKING FOR USER IN USERS TABLE ---*
       1000-MAIN-PARA.
            MOVE LOW-VALUES TO USERS-REC.
            MOVE LS-USER-ID TO DB-USERID.
            EXEC SQL
                 SELECT PASSWD INTO
                 :DB-PASSWD FROM USERS
                 WHERE USERID = :DB-USERID
            END-EXEC.
            EVALUATE SQLCODE
            WHEN 0
                PERFORM 2000-VERIFY-ID-PASS-PARA
                PERFORM 3000-END-PGM-PARA
            WHEN OTHER
                MOVE 0 TO LS-VALID-FLAG
            END-EVALUATE.
       2000-VERIFY-ID-PASS-PARA.
            IF NOT ( DB-PASSWD = LOW-VALUES ) THEN
               IF ( LS-USER-PASS = DB-PASSWD ) THEN
                   MOVE 1 TO LS-VALID-FLAG
               ELSE
                   MOVE 2 TO LS-VALID-FLAG
               END-IF
            ELSE
                   MOVE 3 TO LS-VALID-FLAG
            END-IF.
       3000-END-PGM-PARA.
            EXEC CICS RETURN END-EXEC.
