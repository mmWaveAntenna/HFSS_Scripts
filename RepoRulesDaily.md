cd HFSS_TRL_script              # зайти в сабмодуль
git status                      # посмотреть, что изменилось
git add -A
git commit -m "что сделал"
git push origin HEAD            # ← уходит в HFSS_TRL_script.git

cd ..                           # вернуться в корень
git add HFSS_TRL_script         # зафиксировать новый указатель сабмодуля
git commit -m "Bump submodule"
git push -u origin main         # ← уходит в HFSS_Scripts.git