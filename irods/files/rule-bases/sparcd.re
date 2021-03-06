# These are the custom rules for the Sparc'd project

@include "sparcd-env"

_sparcd_PERM = 'own'

_sparcd_logMsg(*Msg) {
  writeLine('serverLog', 'SPARCD: *Msg');
}


_sparcd_notify(*Subject, *Body) {
  if (0 != errorcode(msiSendMail(sparcd_REPORT_EMAIL_ADDR, *Subject, *Body))) {
    writeLine('serverLog', 'SPARCD: failed to send notification');
  }
}


_sparcd_ingest(*Uploader, *TarPath) {
  _sparcd_logMsg('ingesting *TarPath for *Uploader');

  *zoneArg = execCmdArg(ipc_ZONE);
  *adminArg = execCmdArg(sparcd_ADMIN);
  *uploaderArg = execCmdArg(*Uploader);
  *tarArg = execCmdArg(*TarPath);
  *args = "*zoneArg *adminArg *uploaderArg *tarArg";
  *status = errormsg(msiExecCmd("sparcd-ingest", *args, "null", *TarPath, "null", *out), *err);

  *coll = trimr(*TarPath, '-');
  *url = 'https://' ++ _WEBDAV_HOST ++ '/dav' ++ *coll ++ '/';   

  if (*status == 0) {
    _sparcd_notify(
      "SPARC'd ingest success for *TarPath", 
      "*Uploader successfully ingested the image bundle *TarPath into *coll (*url)." );
  } else {
    _sparcd_logMsg(*err);
    msiGetStderrInExecCmdOut(*out, *resp);

    foreach (*err in split(*resp, '\n')) {
      _sparcd_logMsg(*err);
    }

    *notificationBody =
      "*Uploader failed to completely ingest the image bundle *TarPath into *coll (*url). The " ++
      "error is as follows.\n" ++
      "\n" ++ 
      *resp;

    _sparcd_notify("SPARC'd ingest failure for *TarPath", *notificationBody);
    failmsg(*status, 'SPARCD: failed to fully ingest *TarPath');
  }
}


_sparcd_isForSparcd(*Path) =
  let *strBase = str(sparcd_BASE_COLL) in *strBase != '' && *Path like *strBase ++ '/*'


_sparcd_handle_new_object(*User, *Object) {
  if (_sparcd_isForSparcd(*Object)) {
    ipc_giveAccessObj(sparcd_ADMIN, _sparcd_PERM, *Object);

    if (*Object like regex '^' ++ str(sparcd_BASE_COLL) ++ '/[^/]*/Uploads/[^/]*\\.tar$') {
      remote(ipc_RE_HOST, '') {
        _sparcd_logMsg('scheduling ingest of *Object for *User');

# XXX - The rule engine plugin must be specified. This is fixed in iRODS 4.2.9. See 
#       https://github.com/irods/irods/issues/5413.
        #delay("<PLUSET>1s</PLUSET><EF>1s REPEAT 0 TIMES</EF>")
        delay(
          ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
            <PLUSET>1s</PLUSET>
            <EF>1s REPEAT 0 TIMES</EF> ' )
        {_sparcd_ingest(*User, *Object);}
      }
    }
  }
}


sparcd_acPostProcForCollCreate {
  if (_sparcd_isForSparcd($collName)) {
    ipc_giveAccessColl(sparcd_ADMIN, _sparcd_PERM, $collName);
  }
}


sparcd_dataObjCreated(*User, *_, *DATA_OBJ_INFO) {
  _sparcd_handle_new_object(*User, *DATA_OBJ_INFO.logical_path);
}
