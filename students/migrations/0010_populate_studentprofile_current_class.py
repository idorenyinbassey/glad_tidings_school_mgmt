from django.db import migrations


def populate_studentprofile_current_class(apps, schema_editor):
    StudentClass = apps.get_model('results', 'StudentClass')
    # We'll use raw SQL to read the potential leftover text column 'current_class'
    # and populate the FK column 'current_class_id' where it's NULL.
    conn = schema_editor.connection
    cursor = conn.cursor()

    # Attempt to select rows; if the textual column 'current_class' does not exist
    # the SELECT will fail and we'll skip.
    try:
        cursor.execute("SELECT id, current_class, current_class_id FROM students_studentprofile")
    except Exception:
        # nothing to do if the column isn't present
        return

    rows = cursor.fetchall()
    unmatched = {}
    updated = 0
    for row in rows:
        row_id, raw_current, cur_id = row[0], row[1], row[2]
        if cur_id is not None:
            continue
        if not raw_current:
            continue
        name = str(raw_current).strip()
        if not name:
            continue
        # try case-insensitive exact match first
        sc = StudentClass.objects.filter(name__iexact=name).first()
        if not sc:
            # try looser matching: strip extra whitespace and compare
            condensed = ' '.join(name.split())
            sc = StudentClass.objects.filter(name__iexact=condensed).first()
        if sc:
            cursor.execute("UPDATE students_studentprofile SET current_class_id = ? WHERE id = ?", [sc.id, row_id])
            updated += 1
        else:
            unmatched.setdefault(name, 0)
            unmatched[name] += 1

    # Print a short summary so migration output shows what happened.
    print(f"populate_studentprofile_current_class: updated={updated}, unmatched_names={len(unmatched)}")
    if unmatched:
        print("Unmatched class names (sample):")
        for k, v in list(unmatched.items())[:20]:
            print(f" - {k}: {v} rows")


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0009_alter_academicstatus_current_class'),
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_studentprofile_current_class, reverse_code=migrations.RunPython.noop),
    ]
