"""One useful XB11 shelf with upright WAGO and an open guarded wire window."""
import aux_splice_shelf_r1 as recipe
recipe.OUT=recipe.ROOT/'hardware/cad/studies/aux-splice-shelf-r2'
recipe.MODEL=recipe.OUT/'AuxSpliceShelfR2.FCStd'
recipe.STL=recipe.OUT/'AuxSpliceShelf_R2_candidate_x1.stl'
if __name__=='__main__':recipe.main()
