function doPost(e) {
    var lock = LockService.getScriptLock();
    lock.tryLock(10000);

    try {
        var doc = SpreadsheetApp.getActiveSpreadsheet();
        var sheet = doc.getSheetByName('Yayinlar');

        // Eğer sayfa yoksa oluştur ve başlıkları ekle
        if (!sheet) {
            sheet = doc.insertSheet('Yayinlar');
            var headers = [
                "id", "department", "publication_type", "authors_json", "publication_date", "title",
                "journal_name", "volume", "issue", "pages", "publisher",
                "location", "editors", "book_title", "project_status", "funding_agency",
                "created_at"
            ];
            sheet.appendRow(headers);
        }

        var data = JSON.parse(e.postData.contents);

        // Yeni bir ID oluştur (son satırdaki ID + 1)
        var lastRow = sheet.getLastRow();
        var newId = 1;
        if (lastRow > 1) {
            var lastId = sheet.getRange(lastRow, 1).getValue();
            if (!isNaN(lastId)) {
                newId = lastId + 1;
            }
        }

        var row = [
            newId,
            data.department || "",
            data.publication_type || "",
            JSON.stringify(data.authors) || "[]", // Yazarları JSON string olarak sakla
            data.publication_date || "",
            data.title || "",
            data.journal_name || "",
            data.volume || "",
            data.issue || "",
            data.pages || "",
            data.publisher || "",
            data.location || "",
            data.editors || "",
            data.book_title || "",
            data.project_status || "",
            data.funding_agency || "",
            new Date().toISOString().slice(0, 10) // created_at (YYYY-MM-DD)
        ];

        sheet.appendRow(row);

        return ContentService
            .createTextOutput(JSON.stringify({ "result": "success", "id": newId }))
            .setMimeType(ContentService.MimeType.JSON);

    } catch (e) {
        return ContentService
            .createTextOutput(JSON.stringify({ "result": "error", "error": e }))
            .setMimeType(ContentService.MimeType.JSON);
    } finally {
        lock.releaseLock();
    }
}

function doGet(e) {
    var lock = LockService.getScriptLock();
    lock.tryLock(10000);

    try {
        var doc = SpreadsheetApp.getActiveSpreadsheet();
        var sheet = doc.getSheetByName('Yayinlar');

        if (!sheet) {
            return ContentService
                .createTextOutput(JSON.stringify([]))
                .setMimeType(ContentService.MimeType.JSON);
        }

        var data = sheet.getDataRange().getValues();
        var headers = data[0];
        var jsonData = [];

        // 1. satır başlıklar, 2. satırdan itibaren veriler
        for (var i = 1; i < data.length; i++) {
            var row = data[i];
            var record = {};

            for (var j = 0; j < headers.length; j++) {
                var header = headers[j];
                var value = row[j];

                // authors_json alanını tekrar nesneye çevir
                if (header === "authors_json" && value) {
                    try {
                        record['authors'] = JSON.parse(value);
                    } catch (err) {
                        record['authors'] = [];
                    }
                } else {
                    record[header] = value;
                }
            }
            // 'authors' zaten işlendi, 'authors_json' key'ine gerek yok veya tutabiliriz.
            // Python tarafı 'authors' bekliyor.
            jsonData.push(record);
        }

        return ContentService
            .createTextOutput(JSON.stringify(jsonData))
            .setMimeType(ContentService.MimeType.JSON);

    } catch (e) {
        return ContentService
            .createTextOutput(JSON.stringify({ "result": "error", "error": e }))
            .setMimeType(ContentService.MimeType.JSON);
    } finally {
        lock.releaseLock();
    }
}
